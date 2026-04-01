import streamlit as st

st.set_page_config(page_title="Dashboard", layout="wide")

pg = st.navigation(
    [
        st.Page("pages/1_Global Prices.py", title="Global Prices", default=True),
        st.Page("pages/2_Singapore Prices.py", title="Singapore Prices"),
        st.Page("pages/3_Sector-specific Indicators.py", title="Sector-specific Indicators"),
    ],
    position="sidebar",
)

pg.run()
