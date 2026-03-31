import streamlit as st
import plotly.express as px

from src.csv_loader import load_chart_from_csv
from src.series_config import HIGH_FREQUENCY_SECTOR_INDICATORS, DATA_FILES

st.title("High-frequency Sector Indicators")

CSV_PATH = "data/Water Transport.csv"


def make_y_label(unit: str) -> str:
    if unit == "%":
        return "Percent (%)"
    elif unit:
        return unit
    return "Value"


for section_name, charts in HIGH_FREQUENCY_SECTOR_INDICATORS.items():
    st.header(section_name)

    csv_path = DATA_FILES.get(section_name)

    if not csv_path:
        st.warning(f"No CSV defined for {section_name}")
        continue

    for chart_title, series_columns in charts.items():
        df, unit = load_chart_from_csv(csv_path, series_columns)

        if df.empty:
            st.warning(f"No data returned for {chart_title}.")
            continue

        fig = px.line(
            df,
            x="date",
            y="value",
            color="series_name",
            title=chart_title,
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title=make_y_label(unit),
            hovermode="x unified",
        )

        st.plotly_chart(fig, use_container_width=True)