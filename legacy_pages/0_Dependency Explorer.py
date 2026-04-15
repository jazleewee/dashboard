from __future__ import annotations

from collections.abc import Iterable

import pandas as pd
import streamlit as st

from src.charts import build_line_chart
from src.dependency_config import DEPENDENCY_NODES, ROOT_NODES
from src.data_loader import load_series
from src.google_sheets_client import SHEET_TABS, get_default_spreadsheet_id, load_google_sheet_tabs
from src.series_config import SERIES_REGISTRY


st.set_page_config(page_title="Dependency Explorer", layout="wide")
st.title("Energy Transmission Mindmap")
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
    for index, node_id in enumerate(node_ids):
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
    explicit_ids = list(node.get("series_ids", []))
    terms = get_node_terms(node_id)
    matched_ids = list(explicit_ids)

    for series_id, series_def in SERIES_REGISTRY.items():
        if series_def.get("source") != "ceic":
            continue
        label = series_def.get("label", series_id)
        if matches_terms(label, terms) and series_id not in matched_ids:
            matched_ids.append(series_id)

    return matched_ids


def get_matching_google_frames(node_id: str, google_tabs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    terms = get_node_terms(node_id)
    matched_frames: dict[str, pd.DataFrame] = {}

    for sheet_name, df in google_tabs.items():
        if df.empty:
            continue

        series_match = df["series_name"].fillna("").apply(lambda value: matches_terms(value, terms))
        ticker_match = df["ticker"].fillna("").apply(lambda value: matches_terms(value, terms))
        matched_df = df[series_match | ticker_match].copy()

        if not matched_df.empty:
            matched_frames[sheet_name] = matched_df.sort_values(["unit", "series_name", "date"]).reset_index(drop=True)

    return matched_frames


@st.cache_data(ttl=300)
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
        group_key = (normalized_frequency, normalized_unit)
        grouped_frames[group_key] = group_df.sort_values(["series_name", "date"]).reset_index(drop=True)

    for (frequency, unit), group_df in grouped_frames.items():
        title_bits = [base_title, source_label]
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
    (
        "Upstream Inputs",
        "Crude oil and gas supply shocks that start the chain.",
        ["crude_oil", "gas"],
        "#f2e7c8",
    ),
    (
        "Products & Feedstocks",
        "Fuel and gas-linked products that transmit upstream pressure.",
        [
            "marine_fuel",
            "jet_fuel",
            "diesel_petrol",
            "lpg",
            "naphtha",
            "ethane",
            "methane",
            "helium",
        ],
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
        [
            "water_transport",
            "air_transport",
            "land_transport",
            "petrochemicals",
            "basic_chemicals",
            "water_waste",
            "petroleum",
            "gas_electricity",
        ],
        "#d8e9ff",
    ),
    (
        "Indirect Hit Sectors",
        "Second-round sectors exposed through production, utilities, and trade links.",
        [
            "wholesale_bunkering",
            "wholesale_ex_bunkering",
            "construction",
            "real_estate",
            "food_beverage",
            "semiconductors",
        ],
        "#e4e7fb",
    ),
]


selected_node_id = st.session_state.get("selected_dependency_node", ROOT_NODES[0])

with st.expander("Reference Mindmap", expanded=False):
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

path_labels = " -> ".join(get_node(node_id)["label"] for node_id in get_ancestry(selected_node_id))
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

st.markdown("## Indicators")
st.caption("Charts below are grouped automatically from Google Sheets series names and CEIC labels that match the selected node.")

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
