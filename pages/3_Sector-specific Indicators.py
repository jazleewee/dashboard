import streamlit as st

from src.charts import build_line_chart
from src.data_loader import load_chart_data
from src.series_config import SECTOR_SPECIFIC_INDICATORS

st.title("Sector-specific Indicators")

SECTION_DIVIDER_HTML = """
<hr style="
    border: none;
    height: 4px;
    background: linear-gradient(90deg, #111111 0%, #555555 50%, #111111 100%);
    margin: 2.5rem 0 2rem 0;
    border-radius: 999px;
"/>
"""
for index, (section_name, charts) in enumerate(SECTOR_SPECIFIC_INDICATORS.items()):
    if index > 0:
        st.markdown(SECTION_DIVIDER_HTML, unsafe_allow_html=True)

    st.header(section_name)

    for chart_title, series_ids in charts.items():
        df, chart_meta = load_chart_data(series_ids)
        errors = chart_meta.get("errors", [])

        if df.empty:
            if errors:
                for error in errors:
                    st.warning(f"{chart_title}: {error}")
            else:
                st.warning(f"No data returned for {chart_title}.")
            continue

        for error in errors:
            st.warning(f"{chart_title}: {error}")

        fig = build_line_chart(df, chart_title, chart_meta.get("unit", ""), chart_meta.get("frequency", ""))
        st.plotly_chart(fig, use_container_width=True)
