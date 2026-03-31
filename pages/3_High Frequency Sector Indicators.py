import streamlit as st
import plotly.express as px

from src.csv_loader import load_chart_from_csv
from src.series_config import HIGH_FREQUENCY_SECTOR_INDICATORS, DATA_FILES

st.title("High Frequency Sector Indicators")

SECTION_DIVIDER_HTML = """
<hr style="
    border: none;
    height: 4px;
    background: linear-gradient(90deg, #111111 0%, #555555 50%, #111111 100%);
    margin: 2.5rem 0 2rem 0;
    border-radius: 999px;
"/>
"""


def make_y_label(unit: str) -> str:
    if unit == "%":
        return "Percent (%)"
    elif unit:
        return unit
    return "Value"


def make_date_formats(frequency: str) -> tuple[str, str]:
    frequency_text = frequency.lower()
    if "month" in frequency_text:
        return "%b %Y", "%b\n%Y"
    return "%d %b %Y", "%b\n%Y"


for index, (section_name, charts) in enumerate(HIGH_FREQUENCY_SECTOR_INDICATORS.items()):
    if index > 0:
        st.markdown(SECTION_DIVIDER_HTML, unsafe_allow_html=True)

    st.header(section_name)

    csv_path = DATA_FILES.get(section_name)

    if not csv_path:
        st.warning(f"No CSV defined for {section_name}")
        continue

    for chart_title, series_columns in charts.items():
        df, unit, frequency = load_chart_from_csv(csv_path, series_columns)

        if df.empty:
            st.warning(f"No data returned for {chart_title}.")
            continue

        hover_date_format, tick_date_format = make_date_formats(frequency)

        fig = px.line(
            df,
            x="date",
            y="value",
            color="series_name",
            title=chart_title,
            template="plotly_white",
        )

        fig.update_traces(
            line=dict(width=3),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                f"Date: %{{x|{hover_date_format}}}<br>"
                "Value: %{y}<extra></extra>"
            ),
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title=make_y_label(unit),
            hovermode="x unified",
            font=dict(color="black", size=14),
            title=dict(font=dict(color="black", size=22), x=0.02, xanchor="left"),
            legend=dict(
                title=None,
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color="black", size=12),
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=20, r=20, t=80, b=20),
            hoverlabel=dict(
                bgcolor="white",
                bordercolor="#333333",
                font=dict(color="black", size=13),
            ),
        )
        fig.update_xaxes(
            showgrid=True,
            gridcolor="#D9D9D9",
            linecolor="black",
            tickfont=dict(color="black"),
            title_font=dict(color="black"),
            tickformat=tick_date_format,
            hoverformat=hover_date_format,
        )
        fig.update_yaxes(
            showgrid=True,
            gridcolor="#D9D9D9",
            zeroline=False,
            linecolor="black",
            tickfont=dict(color="black"),
            title_font=dict(color="black"),
        )

        st.plotly_chart(fig, use_container_width=True)
