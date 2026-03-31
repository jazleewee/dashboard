from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


def parse_date_series(values: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(values, format="%m/%d/%Y", errors="coerce")

    missing_mask = parsed.isna()
    if missing_mask.any():
        parsed.loc[missing_mask] = pd.to_datetime(
            values.loc[missing_mask],
            format="%m/%Y",
            errors="coerce",
        )

    return parsed


@st.cache_data(ttl=3600)
def _load_chart_from_csv_cached(
    csv_path: str,
    series_columns: list[str],
    file_mtime_ns: int,
) -> tuple[pd.DataFrame, str, str]:
    del file_mtime_ns
    raw = pd.read_csv(csv_path)

    date_col = raw.columns[0]

    # Metadata rows end before the first actual date row
    data_start_idx = None
    for i, value in enumerate(raw[date_col].astype(str)):
        parsed = parse_date_series(pd.Series([value])).iloc[0]
        if pd.notna(parsed):
            data_start_idx = i
            break

    if data_start_idx is None:
        return pd.DataFrame(), "", ""

    # Unit row is in metadata section
    unit_row = raw[raw[date_col] == "Unit"]
    unit = ""
    if not unit_row.empty and len(series_columns) > 0:
        first_unit = unit_row.iloc[0][series_columns[0]]
        if pd.notna(first_unit):
            unit = str(first_unit)

    frequency_row = raw[raw[date_col] == "Frequency"]
    frequency = ""
    if not frequency_row.empty and len(series_columns) > 0:
        first_frequency = frequency_row.iloc[0][series_columns[0]]
        if pd.notna(first_frequency):
            frequency = str(first_frequency)

    data = raw.iloc[data_start_idx:, [0] + [raw.columns.get_loc(c) for c in series_columns]].copy()
    data = data.rename(columns={date_col: "date"})
    data["date"] = parse_date_series(data["date"])

    long_df = data.melt(id_vars="date", var_name="series_name", value_name="value")
    long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")
    long_df = long_df.dropna(subset=["date", "value"]).sort_values(["series_name", "date"]).reset_index(drop=True)

    return long_df, unit, frequency


def load_chart_from_csv(csv_path: str, series_columns: list[str]) -> tuple[pd.DataFrame, str, str]:
    file_mtime_ns = Path(csv_path).stat().st_mtime_ns
    result = _load_chart_from_csv_cached(csv_path, series_columns, file_mtime_ns)

    # Be tolerant of older cached values created before frequency was added.
    if len(result) == 2:
        df, unit = result
        return df, unit, ""

    return result
