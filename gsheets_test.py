from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import build_line_chart
from src.google_sheets_client import (
    SHEET_TABS,
    get_default_spreadsheet_id,
    get_default_spreadsheet_name,
    load_google_sheet_tabs,
)
SECTION_DIVIDER_HTML = """
<hr style="
    border: none;
    height: 4px;
    background: linear-gradient(90deg, #111111 0%, #555555 50%, #111111 100%);
    margin: 2.5rem 0 2rem 0;
    border-radius: 999px;
"/>
"""


st.set_page_config(page_title="Google Sheets Test", layout="wide")
st.title("Google Sheets Test")

default_sheet_name = get_default_spreadsheet_name()
default_spreadsheet_id = get_default_spreadsheet_id()

try:
    if not default_spreadsheet_id:
        raise RuntimeError(
            "Missing GOOGLE_SHEETS_SPREADSHEET_ID in Streamlit secrets. "
            "Add the spreadsheet ID from the Google Sheets URL to .streamlit/secrets.toml."
        )
    tab_frames = load_google_sheet_tabs(default_spreadsheet_id)
except Exception as exc:
    st.error(str(exc))
    st.stop()

st.success(f"Connected to spreadsheet `{default_sheet_name}`.")

for index, sheet_name in enumerate(SHEET_TABS):
    if index > 0:
        st.markdown(SECTION_DIVIDER_HTML, unsafe_allow_html=True)

    st.header(sheet_name)
    df = tab_frames.get(sheet_name, pd.DataFrame())

    if df.empty:
        st.warning(f"No data parsed from the {sheet_name} tab.")
        continue

    series_names = sorted(df["series_name"].dropna().unique())
    selected_series = st.multiselect(
        f"{sheet_name} series",
        options=series_names,
        default=series_names,
        key=f"{sheet_name.lower()}_series",
    )

    filtered_df = df[df["series_name"].isin(selected_series)].copy()
    if filtered_df.empty:
        st.info(f"No series selected for {sheet_name}.")
        continue

    units = [unit for unit in filtered_df["unit"].dropna().unique() if str(unit).strip()]
    if not units:
        units = [""]

    for unit in sorted(units):
        unit_df = filtered_df[filtered_df["unit"].fillna("") == unit].copy()
        if unit_df.empty:
            continue

        chart_title = f"{sheet_name} ({unit})" if unit else sheet_name
        fig = build_line_chart(unit_df, chart_title, unit, sheet_name)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander(f"Preview parsed {sheet_name} data"):
        st.dataframe(filtered_df, use_container_width=True)
