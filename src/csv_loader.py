from __future__ import annotations

import pandas as pd
import streamlit as st


@st.cache_data(ttl=3600)
def load_chart_from_csv(csv_path: str, series_columns: list[str]) -> tuple[pd.DataFrame, str]:
    raw = pd.read_csv(csv_path)

    date_col = raw.columns[0]

    # Metadata rows end before the first actual date row
    data_start_idx = None
    for i, value in enumerate(raw[date_col].astype(str)):
        parsed = pd.to_datetime(value, format="%m/%d/%Y", errors="coerce")
        if pd.notna(parsed):
            data_start_idx = i
            break

    if data_start_idx is None:
        return pd.DataFrame(), ""

    # Unit row is in metadata section
    unit_row = raw[raw[date_col] == "Unit"]
    unit = ""
    if not unit_row.empty and len(series_columns) > 0:
        first_unit = unit_row.iloc[0][series_columns[0]]
        if pd.notna(first_unit):
            unit = str(first_unit)

    data = raw.iloc[data_start_idx:, [0] + [raw.columns.get_loc(c) for c in series_columns]].copy()
    data = data.rename(columns={date_col: "date"})
    data["date"] = pd.to_datetime(data["date"], format="%m/%d/%Y", errors="coerce")

    long_df = data.melt(id_vars="date", var_name="series_name", value_name="value")
    long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")
    long_df = long_df.dropna(subset=["date", "value"]).sort_values(["series_name", "date"]).reset_index(drop=True)

    return long_df, unit