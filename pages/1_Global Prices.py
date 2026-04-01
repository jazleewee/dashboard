import streamlit as st

from src.charts import build_dual_axis_chart, build_line_chart
from src.data_loader import load_chart_data
from src.series_config import GLOBAL_PRICES

st.title("Global Prices")

SECTION_DIVIDER_HTML = """
<hr style="
    border: none;
    height: 4px;
    background: linear-gradient(90deg, #111111 0%, #555555 50%, #111111 100%);
    margin: 2.5rem 0 2rem 0;
    border-radius: 999px;
"/>
"""


for index, (section_name, charts) in enumerate(GLOBAL_PRICES.items()):
    if index > 0:
        st.markdown(SECTION_DIVIDER_HTML, unsafe_allow_html=True)

    st.header(section_name)

    for chart_title, chart_spec in charts.items():
        if "series_ids" in chart_spec:
            df, chart_meta = load_chart_data(chart_spec["series_ids"])
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

            fig = build_line_chart(
                df,
                chart_title,
                chart_meta.get("unit", ""),
                chart_meta.get("frequency", ""),
            )
            st.plotly_chart(fig, use_container_width=True)
            continue

        left_df, left_meta = load_chart_data(chart_spec["left_series_ids"])
        right_df, right_meta = load_chart_data(chart_spec["right_series_ids"])

        left_errors = left_meta.get("errors", [])
        right_errors = right_meta.get("errors", [])
        for error in left_errors + right_errors:
            st.warning(f"{chart_title}: {error}")

        if left_df.empty or right_df.empty:
            st.warning(f"No data returned for {chart_title}.")
            continue

        frequency = left_meta.get("frequency") or right_meta.get("frequency", "")
        fig = build_dual_axis_chart(
            left_df,
            right_df,
            chart_title,
            left_meta.get("unit", ""),
            right_meta.get("unit", ""),
            frequency,
        )
        st.plotly_chart(fig, use_container_width=True)
