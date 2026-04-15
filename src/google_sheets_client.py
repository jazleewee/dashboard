from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


SHEET_TABS = ("Daily", "Weekly", "Monthly")
HEADER_ROW_INDEX = 0
NAME_ROW_INDEX = 1
UNIT_ROW_INDEX = 2
DATA_START_ROW_INDEX = 4
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


def get_secret(name: str, default: str = "") -> str:
    value = st.secrets.get(name, default)
    return str(value).strip() if value is not None else default


def get_default_spreadsheet_name() -> str:
    return get_secret("GOOGLE_SHEETS_NAME", "dashboard data")


def get_default_spreadsheet_id() -> str:
    return get_secret("GOOGLE_SHEETS_SPREADSHEET_ID")


def get_service_account_info() -> dict[str, Any]:
    if "gcp_service_account" in st.secrets:
        return dict(st.secrets["gcp_service_account"])
    raise RuntimeError("Missing [gcp_service_account] in Streamlit secrets.")


@st.cache_resource(show_spinner="Running")
def get_google_credentials() -> Credentials:
    return Credentials.from_service_account_info(get_service_account_info(), scopes=SCOPES)


@st.cache_resource(show_spinner="Running")
def get_sheets_service():
    return build("sheets", "v4", credentials=get_google_credentials(), cache_discovery=False)


@st.cache_data(ttl=300, show_spinner="Running")
def fetch_sheet_values(spreadsheet_id: str, sheet_name: str) -> list[list[str]]:
    result = (
        get_sheets_service()
        .spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=sheet_name)
        .execute()
    )
    return result.get("values", [])


def _pad_rows(rows: list[list[str]]) -> list[list[str]]:
    max_width = max((len(row) for row in rows), default=0)
    return [row + [""] * (max_width - len(row)) for row in rows]


def parse_sheet_tab(sheet_name: str, rows: list[list[str]]) -> pd.DataFrame:
    if len(rows) <= DATA_START_ROW_INDEX:
        return pd.DataFrame()

    padded_rows = _pad_rows(rows)
    header_row = padded_rows[HEADER_ROW_INDEX]
    name_row = padded_rows[NAME_ROW_INDEX]
    unit_row = padded_rows[UNIT_ROW_INDEX]

    records: list[dict[str, Any]] = []
    for col_idx in range(1, len(header_row)):
        ticker = str(header_row[col_idx]).strip()
        series_name = str(name_row[col_idx]).strip() or ticker or f"{sheet_name} Series {col_idx}"
        unit = str(unit_row[col_idx]).strip()

        if not any([ticker, series_name, unit]):
            continue

        for row in padded_rows[DATA_START_ROW_INDEX:]:
            raw_date = str(row[0]).strip()
            raw_value = str(row[col_idx]).strip() if col_idx < len(row) else ""

            if not raw_date or not raw_value:
                continue

            records.append(
                {
                    "date": raw_date,
                    "value": raw_value,
                    "series_name": series_name,
                    "ticker": ticker,
                    "unit": unit,
                    "frequency": sheet_name,
                    "source": "google_sheets",
                    "sheet_name": sheet_name,
                }
            )

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.dropna(subset=["date", "value"]).sort_values(["series_name", "date"]).reset_index(drop=True)


@st.cache_data(ttl=300, show_spinner="Running")
def load_google_sheet_tabs(spreadsheet_id: str) -> dict[str, pd.DataFrame]:
    parsed_tabs: dict[str, pd.DataFrame] = {}
    for sheet_name in SHEET_TABS:
        parsed_tabs[sheet_name] = parse_sheet_tab(sheet_name, fetch_sheet_values(spreadsheet_id, sheet_name))
    return parsed_tabs
