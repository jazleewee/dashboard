from __future__ import annotations

import ast
import re
import time

import pandas as pd
import requests
import streamlit as st


MOTORIST_TREND_URL = "https://www.motorist.sg/petrol-prices"
CHARTKICK_MARKER = 'new Chartkick["LineChart"]("chart-1", '


def _unescape_js_string(value: str) -> str:
    return value.encode("utf-8").decode("unicode_escape")


def _extract_balanced_segment(text: str, start_char: str, end_char: str) -> str:
    start_index = text.find(start_char)
    if start_index == -1:
        raise RuntimeError("Unable to locate the start of the chart data segment.")

    depth = 0
    in_string = False
    string_char = ""
    escaped = False

    for index in range(start_index, len(text)):
        char = text[index]

        if escaped:
            escaped = False
            continue

        if char == "\\":
            escaped = True
            continue

        if in_string:
            if char == string_char:
                in_string = False
            continue

        if char in {"'", '"'}:
            in_string = True
            string_char = char
            continue

        if char == start_char:
            depth += 1
        elif char == end_char:
            depth -= 1
            if depth == 0:
                return text[start_index : index + 1]

    raise RuntimeError("Unable to locate the end of the chart data segment.")


def _extract_chartkick_series(response_text: str) -> list[dict]:
    candidates = [response_text]

    try:
        unescaped_response = _unescape_js_string(response_text)
    except Exception:
        unescaped_response = response_text

    if unescaped_response != response_text:
        candidates.append(unescaped_response)

    for candidate in candidates:
        marker_index = candidate.find(CHARTKICK_MARKER)
        if marker_index == -1:
            continue

        chart_call_tail = candidate[marker_index + len(CHARTKICK_MARKER) :]
        series_literal = _extract_balanced_segment(chart_call_tail, "[", "]")
        try:
            return ast.literal_eval(series_literal)
        except Exception:
            try:
                return ast.literal_eval(_unescape_js_string(series_literal))
            except Exception:
                continue

    raise RuntimeError("Unable to locate fuel trend series data in the Motorist response.")


def _series_to_frame(series: list[dict], grade: str) -> pd.DataFrame:
    rows: list[dict] = []

    for brand_series in series:
        brand_name = str(brand_series.get("name", "")).strip() or "Unknown"
        for date_label, value in brand_series.get("data", []):
            rows.append(
                {
                    "date": pd.to_datetime(date_label, format="%d %b %y", errors="coerce"),
                    "value": pd.to_numeric(value, errors="coerce"),
                    "series_name": brand_name,
                    "unit": "SGD/Litre",
                    "frequency": "Daily",
                    "source": "motorist",
                    "grade": grade,
                }
            )

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    return df.dropna(subset=["date", "value"]).sort_values(["series_name", "date"]).reset_index(drop=True)


@st.cache_data(ttl=1800, show_spinner="Running")
def load_fuel_price_trend(grade: str = "92", date_range: int = 6) -> pd.DataFrame:
    params = {
        "grade": grade,
        "date_range": str(date_range),
        "_": str(int(time.time() * 1000)),
    }
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "text/javascript, */*; q=0.01",
        "Referer": MOTORIST_TREND_URL,
    }
    response = requests.get(MOTORIST_TREND_URL, params=params, headers=headers, timeout=20)
    response.raise_for_status()

    series = _extract_chartkick_series(response.text)
    return _series_to_frame(series, grade)
