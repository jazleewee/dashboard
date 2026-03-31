from __future__ import annotations

import pandas as pd
import streamlit as st
from ceic_api_client.pyceic import Ceic

@st.cache_data(ttl=3600)
def fetch_series(series_id: str):
    Ceic.set_token(st.secrets["CEIC_API_KEY"])

    # --- METADATA ---
    meta_result = Ceic.series_metadata(str(series_id))

    label = f"Series {series_id}"
    unit = ""

    if hasattr(meta_result, "data") and len(meta_result.data) > 0:
        meta = meta_result.data[0].metadata

        name = meta.name if hasattr(meta, "name") else ""
        country = meta.country.name if meta.country else ""
        freq = meta.frequency.name if meta.frequency else ""
        unit = meta.unit.name if meta.unit else ""

        label = f"{name} – {country} ({freq})"

    # --- DATA ---
    result = Ceic.series_data(str(series_id))

    if not hasattr(result, "data") or len(result.data) == 0:
        return pd.DataFrame(), label, unit

    series_obj = result.data[0]
    time_points = getattr(series_obj, "time_points", None)

    if not time_points:
        return pd.DataFrame(), label, unit

    rows = []
    for tp in time_points:
        rows.append({
            "date": tp.date,
            "value": tp.value
        })

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.sort_values("date")

    return df, label, unit