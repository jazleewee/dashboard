from __future__ import annotations

from collections.abc import Iterable

import pandas as pd
import plotly.express as px
import streamlit as st

from src.charts import build_line_chart
from src.data_loader import load_series
from src.dependency_config import DEPENDENCY_NODES, ROOT_NODES
from src.motorist_client import load_fuel_price_trend
from src.google_sheets_client import SHEET_TABS, fetch_sheet_values, get_default_spreadsheet_id, load_google_sheet_tabs
from src.series_config import SERIES_REGISTRY


st.set_page_config(page_title="Dashboard", layout="wide")
st.title("Energy Dashboard")
st.caption("Explore how upstream energy disruptions flow through products, sectors, and the indicators attached to them.")

st.markdown(
    """
<style>
div[data-testid="stButton"] > button {
    width: 100%;
    min-height: 2.35rem;
    border-radius: 999px;
    border: 1px solid #0b2f61;
    background: linear-gradient(180deg, #f0d08a 0%, #c29a51 100%);
    color: #111111;
    font-weight: 700;
    font-size: 0.92rem;
    box-shadow: 0 6px 16px rgba(11, 47, 97, 0.12);
    padding: 0.12rem 0.4rem;
}
div[data-testid="stButton"] > button[kind="primary"] {
    border: 3px solid #c11245;
    background: linear-gradient(180deg, #f3d48f 0%, #cea35c 100%);
    box-shadow: 0 0 0 3px rgba(193, 18, 69, 0.22), 0 10px 24px rgba(193, 18, 69, 0.2);
}
div[data-testid="stButton"] > button:hover {
    border-color: #082248;
    transform: translateY(-1px);
}
.mindmap-band {
    padding: 0.55rem 0.55rem 0.65rem 0.55rem;
    border-radius: 0.9rem;
    height: 100%;
}
.mindmap-connector {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 23rem;
}
.mindmap-connector-line {
    position: relative;
    width: 100%;
    height: 0.22rem;
    border-radius: 999px;
    background: linear-gradient(90deg, rgba(11, 47, 97, 0.18) 0%, rgba(11, 47, 97, 0.52) 50%, rgba(11, 47, 97, 0.18) 100%);
}
.mindmap-connector-line::after {
    content: "";
    position: absolute;
    right: -0.15rem;
    top: 50%;
    transform: translateY(-50%);
    border-top: 0.45rem solid transparent;
    border-bottom: 0.45rem solid transparent;
    border-left: 0.7rem solid rgba(11, 47, 97, 0.6);
}
.band-title {
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
    color: #0b2f61;
}
.column-note {
    font-size: 0.78rem;
    line-height: 1.35;
    color: #314567;
    margin-bottom: 0.55rem;
}
.node-meta {
    padding: 1rem 1.1rem;
    border-radius: 1rem;
    background: linear-gradient(180deg, #eef4ff 0%, #d9e6fb 100%);
    border: 1px solid #adc6ef;
    margin-bottom: 1rem;
}
.source-chip {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
    background: #0b2f61;
    color: white;
    font-size: 0.85rem;
    margin-right: 0.4rem;
}
.path-chain {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.35rem;
    margin-top: 0.55rem;
}
.path-node {
    display: inline-flex;
    align-items: center;
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    background: white;
    border: 1px solid #a8bbdc;
    color: #0b2f61;
    font-size: 0.88rem;
    font-weight: 600;
}
.path-node-current {
    border: 2px solid #c11245;
    color: #8d1038;
    box-shadow: 0 0 0 2px rgba(193, 18, 69, 0.12);
}
.path-arrow {
    color: #55739f;
    font-size: 1rem;
    font-weight: 700;
}
.g-gtitle {
    display: none !important;
}
</style>
""",
    unsafe_allow_html=True,
)


def get_node(node_id: str) -> dict:
    return DEPENDENCY_NODES[node_id]


def get_parent_lookup() -> dict[str, str]:
    parent_lookup: dict[str, str] = {}
    for node_id, node in DEPENDENCY_NODES.items():
        for child_id in node.get("children", []):
            parent_lookup[child_id] = node_id
    return parent_lookup


PARENT_LOOKUP = get_parent_lookup()


def get_ancestry(node_id: str) -> list[str]:
    chain = [node_id]
    while chain[0] in PARENT_LOOKUP:
        chain.insert(0, PARENT_LOOKUP[chain[0]])
    return chain


def render_node_row(node_ids: Iterable[str], selected_node_id: str, row_key: str) -> str:
    node_ids = list(node_ids)
    if not node_ids:
        return selected_node_id
    for node_id in node_ids:
        node = get_node(node_id)
        button_type = "primary" if node_id == selected_node_id else "secondary"

        if st.button(
            node["label"],
            key=f"{row_key}_{node_id}",
            use_container_width=True,
            type=button_type,
        ):
            st.session_state["selected_dependency_node"] = node_id
            st.rerun()

    return selected_node_id


def get_node_terms(node_id: str) -> list[str]:
    node = get_node(node_id)
    terms = [node.get("label", ""), *node.get("sheet_keywords", []), *node.get("ceic_keywords", [])]
    cleaned_terms = []
    for term in terms:
        normalized = str(term).strip().lower()
        if normalized and normalized not in cleaned_terms:
            cleaned_terms.append(normalized)
    return cleaned_terms


def matches_terms(value: str, terms: list[str]) -> bool:
    normalized = str(value).strip().lower()
    return bool(normalized) and any(term in normalized for term in terms)


def get_matching_ceic_series_ids(node_id: str) -> list[str]:
    node = get_node(node_id)
    explicit_ids = [series_id for series_id in node.get("series_ids", []) if series_id in SERIES_REGISTRY]
    explicit_labels = {str(value).strip().lower() for value in node.get("ceic_labels", []) if str(value).strip()}

    if not explicit_labels:
        return explicit_ids

    matched_ids = list(explicit_ids)
    for series_id, series_def in SERIES_REGISTRY.items():
        if series_def.get("source") != "ceic":
            continue
        label = str(series_def.get("label", series_id)).strip().lower()
        if label in explicit_labels and series_id not in matched_ids:
            matched_ids.append(series_id)

    return matched_ids


def normalize_exact_values(values: list[str]) -> set[str]:
    return {str(value).strip().lower() for value in values if str(value).strip()}


def get_matching_google_frames(node_id: str, google_tabs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    node = get_node(node_id)
    explicit_series = normalize_exact_values(node.get("google_sheet_series", []))
    matched_frames: dict[str, pd.DataFrame] = {}

    if not explicit_series:
        return matched_frames

    for sheet_name, df in google_tabs.items():
        if df.empty:
            continue

        normalized_series = df["series_name"].fillna("").astype(str).str.strip().str.lower()
        series_match = normalized_series.isin(explicit_series)

        matched_df = df[series_match].copy()

        if not matched_df.empty:
            matched_frames[sheet_name] = matched_df.sort_values(["unit", "series_name", "date"]).reset_index(drop=True)

    return matched_frames


@st.cache_data(ttl=300, show_spinner="Running")
def load_ceic_frames_for_series(series_ids: tuple[str, ...]) -> tuple[dict[str, pd.DataFrame], list[str]]:
    frames_by_series: dict[str, pd.DataFrame] = {}
    errors: list[str] = []

    for series_id in series_ids:
        series_def = SERIES_REGISTRY.get(series_id)
        if not series_def:
            errors.append(f"Unknown CEIC series id '{series_id}'.")
            continue

        try:
            series_df, meta = load_series(series_def)
        except Exception as exc:
            errors.append(f"{series_def.get('label', series_id)}: {exc}")
            continue

        if meta.get("status") == "error":
            errors.append(meta.get("message", f"Unable to load {series_def.get('label', series_id)}."))
            continue

        if not series_df.empty:
            frames_by_series[series_id] = series_df

    return frames_by_series, errors


def render_grouped_charts(df: pd.DataFrame, base_title: str, source_label: str) -> None:
    if df.empty:
        st.info(f"No {source_label} data matched this node.")
        return

    grouped_frames: dict[tuple[str, str], pd.DataFrame] = {}
    for (frequency, unit), group_df in df.groupby(["frequency", "unit"], dropna=False):
        normalized_frequency = str(frequency).strip() if pd.notna(frequency) else ""
        normalized_unit = str(unit).strip() if pd.notna(unit) else ""
        grouped_frames[(normalized_frequency, normalized_unit)] = group_df.sort_values(
            ["series_name", "date"]
        ).reset_index(drop=True)

    for (frequency, unit), group_df in grouped_frames.items():
        title_bits = []
        if frequency:
            title_bits.append(frequency)
        if unit:
            title_bits.append(unit)
        chart_title = " | ".join(title_bits)
        fig = build_line_chart(group_df, chart_title, unit, frequency)
        st.plotly_chart(fig, use_container_width=True)


def build_ceic_dataframe(series_ids: list[str]) -> tuple[pd.DataFrame, list[str]]:
    if not series_ids:
        return pd.DataFrame(), []

    frames_by_series, errors = load_ceic_frames_for_series(tuple(series_ids))
    if not frames_by_series:
        return pd.DataFrame(), errors

    combined = pd.concat(frames_by_series.values(), ignore_index=True)
    return combined.sort_values(["unit", "frequency", "series_name", "date"]).reset_index(drop=True), errors


MINDMAP_COLUMNS = [
    ("Upstream Inputs", "Crude oil and gas supply shocks that start the chain.", ["crude_oil", "gas"], "#f2e7c8"),
    (
        "Products & Feedstocks",
        "Fuel and gas-linked products that transmit upstream pressure.",
        ["marine_fuel", "jet_fuel", "diesel_petrol", "lpg", "naphtha", "ethane", "methane", "helium"],
        "#f8edd9",
    ),
    (
        "Chemical Derivatives",
        "Olefins, derivative products, and fertilisers as industrial channels.",
        ["olefins_aromatics", "other_derivatives", "fertilisers"],
        "#eef3ff",
    ),
    (
        "Direct Hit Sectors",
        "Sectors hit most directly by the energy and chemicals transmission path.",
        ["water_transport", "air_transport", "land_transport", "petrochemicals", "basic_chemicals", "water_waste", "petroleum", "gas_electricity"],
        "#d8e9ff",
    ),
    (
        "Indirect Hit Sectors",
        "Second-round sectors exposed through production, utilities, and trade links.",
        ["wholesale_bunkering", "wholesale_ex_bunkering", "construction", "real_estate", "food_beverage", "semiconductors"],
        "#e4e7fb",
    ),
]

PRODUCT_LABELS = {
    "2709": "2709: Crude Oil",
    "271012": "271012: Light Oils / Petrol",
    "271019": "271019: Other Petroleum Oils",
    "271111": "271111: Liquefied Natural Gas",
    "271112": "271112: Propane",
    "271113": "271113: Butanes",
    "271121": "271121: Natural Gas in Gaseous State",
}


@st.cache_data(ttl=1800, show_spinner="Running")
def load_trade_data(spreadsheet_id: str) -> pd.DataFrame:
    rows = fetch_sheet_values(spreadsheet_id, "Trade")
    if not rows:
        return pd.DataFrame()

    header, data = rows[0], rows[1:]
    df = pd.DataFrame(data, columns=header)
    if df.empty:
        return df

    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df["TradeValue in 1000 USD"] = pd.to_numeric(df["TradeValue in 1000 USD"], errors="coerce")
    for column in ["ProductCode", "TradeFlowName", "PartnerName", "PartnerISO3"]:
        df[column] = df[column].astype(str).str.strip()

    return df.dropna(subset=["Year", "TradeValue in 1000 USD"]).reset_index(drop=True)


def prepare_trade_share_data(
    trade_df: pd.DataFrame,
    *,
    product_code: str,
    trade_flow: str,
    years: list[int],
    top_n: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    filtered = trade_df[
        (trade_df["ProductCode"] == product_code)
        & (trade_df["TradeFlowName"] == trade_flow)
        & (trade_df["Year"].isin(years))
        & (trade_df["PartnerName"] != "World")
    ].copy()

    if filtered.empty:
        return pd.DataFrame(), pd.DataFrame()

    grouped = (
        filtered.groupby(["Year", "PartnerName"], as_index=False)["TradeValue in 1000 USD"]
        .sum()
        .sort_values(["Year", "TradeValue in 1000 USD"], ascending=[True, False])
    )

    latest_year = max(years)
    ranking = (
        grouped[grouped["Year"] == latest_year]
        .sort_values("TradeValue in 1000 USD", ascending=False)["PartnerName"]
        .tolist()
    )
    top_partners = ranking[:top_n]

    grouped["PartnerGroup"] = grouped["PartnerName"].where(grouped["PartnerName"].isin(top_partners), "Other")
    chart_df = (
        grouped.groupby(["Year", "PartnerGroup"], as_index=False)["TradeValue in 1000 USD"]
        .sum()
        .sort_values(["Year", "TradeValue in 1000 USD"], ascending=[True, False])
    )
    chart_df["YearLabel"] = chart_df["Year"].astype(str)
    chart_df["Share"] = chart_df.groupby("Year")["TradeValue in 1000 USD"].transform(lambda s: s / s.sum() * 100)

    detail_df = grouped.copy()
    detail_df["Share"] = detail_df.groupby("Year")["TradeValue in 1000 USD"].transform(lambda s: s / s.sum() * 100)
    detail_df = detail_df.sort_values(["Year", "TradeValue in 1000 USD"], ascending=[True, False]).reset_index(drop=True)
    return chart_df, detail_df


def get_trade_recommendations(trade_df: pd.DataFrame) -> pd.DataFrame:
    if trade_df.empty:
        return pd.DataFrame()

    imports_only = trade_df[
        (trade_df["TradeFlowName"] == "Gross Imp.") & (trade_df["PartnerName"] != "World")
    ].copy()
    if imports_only.empty:
        return pd.DataFrame()

    summary = (
        imports_only.groupby("ProductCode", as_index=False)["TradeValue in 1000 USD"]
        .sum()
        .sort_values("TradeValue in 1000 USD", ascending=False)
        .reset_index(drop=True)
    )
    summary["ProductLabel"] = summary["ProductCode"].map(lambda code: PRODUCT_LABELS.get(code, code))
    return summary


def render_supply_linkages_view() -> None:
    selected_node_id = st.session_state.get("selected_dependency_node", ROOT_NODES[0])

    with st.expander("Reference Flowchart", expanded=False):
        image_left, image_center, image_right = st.columns([0.12, 0.76, 0.12])
        with image_center:
            st.image("mindmap.png", use_container_width=True)

    st.caption("Click any bubble in the left-to-right transmission map to update the indicator panel below.")

    layout_widths = [1, 0.22, 1.3, 0.22, 1.05, 0.22, 1.25, 0.22, 1.1]
    layout_columns = st.columns(layout_widths, gap="small")

    for column_index, (title, note, node_ids, background) in enumerate(MINDMAP_COLUMNS):
        layout_position = column_index * 2
        with layout_columns[layout_position]:
            st.markdown(
                f'<div class="mindmap-band" style="background:{background};"><div class="band-title">{title}</div><div class="column-note">{note}</div>',
                unsafe_allow_html=True,
            )
            selected_node_id = render_node_row(node_ids, selected_node_id, f"mindmap_{column_index}")
            st.markdown("</div>", unsafe_allow_html=True)

        if column_index < len(MINDMAP_COLUMNS) - 1:
            with layout_columns[layout_position + 1]:
                st.markdown(
                    '<div class="mindmap-connector"><div class="mindmap-connector-line"></div></div>',
                    unsafe_allow_html=True,
                )

    st.session_state["selected_dependency_node"] = selected_node_id
    selected_node = get_node(selected_node_id)

    path_nodes = get_ancestry(selected_node_id)
    path_markup_parts = ['<div style="margin-top: 0.75rem;"><strong>Dependency Path</strong></div>', '<div class="path-chain">']
    for index, node_id in enumerate(path_nodes):
        node_label = get_node(node_id)["label"]
        node_class = "path-node path-node-current" if node_id == selected_node_id else "path-node"
        path_markup_parts.append(f'<span class="{node_class}">{node_label}</span>')
        if index < len(path_nodes) - 1:
            path_markup_parts.append('<span class="path-arrow">→</span>')
    path_markup_parts.append("</div>")
    path_markup = "".join(path_markup_parts)
    st.markdown(
        f"""
    <div class="node-meta">
        <div><span class="source-chip">Selected Node</span><strong>{selected_node['label']}</strong></div>
        <div style="margin-top: 0.6rem;">{selected_node.get('description', '')}</div>
        {path_markup}
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(f"## Indicators for {selected_node['label']}")

    ceic_series_ids = get_matching_ceic_series_ids(selected_node_id)
    ceic_df, ceic_errors = build_ceic_dataframe(ceic_series_ids)

    google_df = pd.DataFrame()
    google_errors: list[str] = []
    google_spreadsheet_id = get_default_spreadsheet_id()
    if google_spreadsheet_id:
        try:
            google_tabs = load_google_sheet_tabs(google_spreadsheet_id)
            matched_google_frames = get_matching_google_frames(selected_node_id, google_tabs)
            google_frames = [matched_google_frames[sheet_name] for sheet_name in SHEET_TABS if sheet_name in matched_google_frames]
            if google_frames:
                google_df = pd.concat(google_frames, ignore_index=True).sort_values(
                    ["frequency", "unit", "series_name", "date"]
                ).reset_index(drop=True)
        except Exception as exc:
            google_errors.append(str(exc))

    for error in ceic_errors + google_errors:
        st.warning(error)

    if ceic_df.empty and google_df.empty:
        st.info("No charts are mapped to this node yet.")
    else:
        if not google_df.empty:
            render_grouped_charts(google_df, selected_node["label"], "Google Sheets")

        if not ceic_df.empty:
            render_grouped_charts(ceic_df, selected_node["label"], "CEIC")

    if selected_node_id == "land_transport":
        st.markdown("### Fuel Prices Trend")
        try:
            fuel_grade_labels = {"92": "92", "95": "95", "98": "98", "premium": "Premium", "diesel": "Diesel"}
            fuel_date_range_labels = {6: "6 months", 12: "12 months", 24: "24 months"}

            selected_grade = st.segmented_control(
                "Fuel Type",
                options=list(fuel_grade_labels.keys()),
                default="92",
                format_func=lambda value: fuel_grade_labels[value],
                key="land_transport_fuel_grade",
            )
            selected_date_range = st.segmented_control(
                "Date Range",
                options=list(fuel_date_range_labels.keys()),
                default=6,
                format_func=lambda value: fuel_date_range_labels[value],
                key="land_transport_date_range",
            )

            fuel_trend_df = load_fuel_price_trend(grade=selected_grade, date_range=selected_date_range)
            if fuel_trend_df.empty:
                st.info("No fuel price trend data was returned.")
            else:
                fuel_fig = build_line_chart(fuel_trend_df, "", "SGD/Litre", "Daily")
                st.plotly_chart(fuel_fig, use_container_width=True)
        except Exception as exc:
            st.warning(f"Unable to load fuel price trend data: {exc}")


def render_trade_view() -> None:
    st.markdown("## Trade")
    st.caption("Explore Singapore's import or export country shares by product over 2022 to 2024.")

    spreadsheet_id = get_default_spreadsheet_id()
    if not spreadsheet_id:
        st.info("Google Sheets is not configured.")
        return

    try:
        trade_df = load_trade_data(spreadsheet_id)
    except Exception as exc:
        st.warning(f"Unable to load Trade data: {exc}")
        return

    if trade_df.empty:
        st.info("No Trade data was returned.")
        return

    recommendations = get_trade_recommendations(trade_df)
    if not recommendations.empty:
        recommended_labels = recommendations.head(3)["ProductLabel"].tolist()
        st.info(
            "Recommended starting products: "
            + ", ".join(recommended_labels)
            + ". These are the largest non-World import categories in the Trade sheet, so they should give the clearest first read on supplier concentration."
        )

    available_products = [code for code in PRODUCT_LABELS if code in set(trade_df["ProductCode"].unique())]
    flow_labels = {"Gross Imp.": "Imports", "Gross Exp.": "Exports"}
    years_available = sorted(int(year) for year in trade_df["Year"].dropna().unique())

    controls = st.columns([1.45, 1, 0.9, 1.1])
    selected_product = controls[0].selectbox(
        "Product",
        options=available_products,
        format_func=lambda code: PRODUCT_LABELS.get(code, code),
        index=0,
    )
    selected_flow = controls[1].segmented_control(
        "Trade Flow",
        options=list(flow_labels.keys()),
        default="Gross Imp.",
        format_func=lambda flow: flow_labels[flow],
    )
    top_n = controls[2].segmented_control("Top Countries", options=[5, 10, 15], default=10)
    selected_years = controls[3].multiselect("Years", options=years_available, default=years_available)

    if not selected_years:
        st.info("Select at least one year.")
        return

    chart_df, detail_df = prepare_trade_share_data(
        trade_df,
        product_code=selected_product,
        trade_flow=selected_flow,
        years=selected_years,
        top_n=int(top_n),
    )

    if chart_df.empty:
        st.info("No trade rows matched the selected filters.")
        return

    selected_label = PRODUCT_LABELS.get(selected_product, selected_product)
    st.caption(
        f"Showing {flow_labels[selected_flow].lower()} country shares for {selected_label}. "
        "The World aggregate is excluded so the shares sum correctly across partner countries."
    )

    chart_title = f"{flow_labels[selected_flow]} Shares by Country"
    fig = px.bar(
        chart_df,
        x="YearLabel",
        y="Share",
        color="PartnerGroup",
        text_auto=".1f",
        template="plotly_white",
        category_orders={"YearLabel": [str(year) for year in selected_years]},
    )
    fig.update_layout(
        title=dict(text=chart_title, x=0.02, xanchor="left"),
        barmode="stack",
        yaxis_title="Share of Total (%)",
        xaxis_title="Year",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Share: %{y:.2f}%<br>Value: %{customdata:,.0f}<extra></extra>",
        customdata=chart_df["TradeValue in 1000 USD"],
    )
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    st.plotly_chart(fig, use_container_width=True)

    latest_year = max(selected_years)
    latest_chart_slice = chart_df[chart_df["Year"] == latest_year].copy()
    latest_chart_slice = latest_chart_slice.sort_values("Share", ascending=False).reset_index(drop=True)
    total_latest_value = latest_chart_slice["TradeValue in 1000 USD"].sum()
    top_country = latest_chart_slice.iloc[0]["PartnerGroup"]
    top_country_share = latest_chart_slice.iloc[0]["Share"]

    metric_left, metric_mid, metric_right = st.columns(3)
    metric_left.metric(f"{latest_year} Total", f"USD {total_latest_value:,.0f}k")
    metric_mid.metric("Largest Country Share", f"{top_country_share:.1f}%")
    metric_right.metric("Largest Country", str(top_country))

    latest_table = detail_df[detail_df["Year"] == latest_year].copy()
    latest_table = latest_table.rename(
        columns={
            "PartnerName": "Country",
            "TradeValue in 1000 USD": "Trade Value (USD '000)",
            "Share": "Share (%)",
        }
    )
    latest_table["Trade Value (USD '000)"] = latest_table["Trade Value (USD '000)"].map(lambda value: f"{value:,.0f}")
    latest_table["Share (%)"] = latest_table["Share (%)"].map(lambda value: f"{value:.2f}")
    st.markdown(f"### {flow_labels[selected_flow]} by Country in {latest_year}")
    st.dataframe(
        latest_table[["Country", "Trade Value (USD '000)", "Share (%)"]].reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )


dashboard_tab, trade_tab = st.tabs(["Supply Linkages", "Trade"])
with dashboard_tab:
    render_supply_linkages_view()
with trade_tab:
    render_trade_view()
