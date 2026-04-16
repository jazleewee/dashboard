from __future__ import annotations

import os
from datetime import datetime, timezone

import pandas as pd
import streamlit as st
from ceic_api_client.pyceic import Ceic


def _read_secret(*names: str) -> str:
    for name in names:
        if name in st.secrets and st.secrets[name]:
            return str(st.secrets[name])
        env_value = os.environ.get(name, "").strip()
        if env_value:
            return env_value
    return ""


def _extract_name(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    for attr in ("name", "label", "value"):
        nested = getattr(value, attr, None)
        if isinstance(nested, str) and nested.strip():
            return nested.strip()
    return ""


def authenticate_ceic() -> None:
    username = _read_secret("CEIC_USERNAME", "CEIC_EMAIL")
    password = _read_secret("CEIC_PASSWORD")
    if username and password:
        try:
            Ceic.login(username, password)
        except Exception as exc:
            raise RuntimeError(_format_ceic_error("CEIC", "", exc, during="login")) from exc
        return

    raise RuntimeError(
        "Missing CEIC credentials. Set CEIC_USERNAME (or CEIC_EMAIL) and CEIC_PASSWORD in Streamlit secrets or environment variables."
    )


@st.cache_resource(show_spinner="Running")
def ensure_ceic_session() -> None:
    authenticate_ceic()


def _format_ceic_error(label: str, series_id: str, exc: Exception, *, during: str) -> str:
    raw_message = str(exc).strip() or exc.__class__.__name__
    normalized = raw_message.lower()
    subject = label or f"series {series_id}"

    if "403" in normalized or "forbidden" in normalized:
        if during == "login":
            return (
                "CEIC login was denied (403). Check the deployed CEIC_USERNAME/CEIC_EMAIL and "
                "CEIC_PASSWORD values."
            )
        return (
            f"{subject}: CEIC denied access (403) for series {series_id}. "
            "The deployed CEIC account may not have permission for this series, or the deployment "
            "is using the wrong CEIC credentials."
        )

    if during == "metadata":
        return f"{subject}: unable to load CEIC metadata. {raw_message}"

    return f"{subject}: unable to load CEIC data. {raw_message}"


@st.cache_data(ttl=3600, show_spinner="Running")
def fetch_series(
    series_id: str,
    label: str = "",
    unit: str = "",
    frequency: str = "",
) -> tuple[pd.DataFrame, dict[str, str]]:
    ensure_ceic_session()

    resolved_label = label or f"Series {series_id}"
    resolved_unit = unit
    resolved_frequency = frequency

    try:
        data_result = Ceic.series_data(str(series_id))
    except Exception as exc:
        raise RuntimeError(_format_ceic_error(resolved_label, series_id, exc, during="data")) from exc

    needs_metadata = not (label and unit and frequency)
    if needs_metadata:
        try:
            meta_result = Ceic.series_metadata(str(series_id))
            if hasattr(meta_result, "data") and meta_result.data:
                metadata = meta_result.data[0].metadata
                resolved_label = label or _extract_name(getattr(metadata, "name", None)) or resolved_label
                resolved_unit = unit or _extract_name(getattr(metadata, "unit", None))
                resolved_frequency = frequency or _extract_name(getattr(metadata, "frequency", None))
        except Exception as exc:
            if not (resolved_label and resolved_unit and resolved_frequency):
                raise RuntimeError(_format_ceic_error(resolved_label, series_id, exc, during="metadata")) from exc

    freshness = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if not hasattr(data_result, "data") or not data_result.data:
        return pd.DataFrame(), {
            "series_id": series_id,
            "series_name": resolved_label,
            "source": "ceic",
            "unit": resolved_unit,
            "frequency": resolved_frequency,
            "freshness": freshness,
            "status": "error",
            "message": f"No CEIC data returned for series {series_id}.",
        }

    series_obj = data_result.data[0]
    time_points = getattr(series_obj, "time_points", None) or []

    if not time_points:
        return pd.DataFrame(), {
            "series_id": series_id,
            "series_name": resolved_label,
            "source": "ceic",
            "unit": resolved_unit,
            "frequency": resolved_frequency,
            "freshness": freshness,
            "status": "error",
            "message": f"CEIC series {series_id} returned no time points.",
        }

    rows = []
    for tp in time_points:
        rows.append({"date": tp.date, "value": tp.value})

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["date", "value"]).sort_values("date").reset_index(drop=True)

    return df, {
        "series_id": series_id,
        "series_name": resolved_label,
        "source": "ceic",
        "unit": resolved_unit,
        "frequency": resolved_frequency,
        "freshness": freshness,
        "status": "ok",
        "message": "",
    }
