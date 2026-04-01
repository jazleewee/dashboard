from __future__ import annotations

import pandas as pd

from src.ceic_client import fetch_series as fetch_ceic_series
from src.series_config import SERIES_REGISTRY


NORMALIZED_COLUMNS = [
    "date",
    "value",
    "series_id",
    "series_name",
    "source",
    "unit",
    "frequency",
]


def _normalize_series_frame(
    df: pd.DataFrame,
    *,
    series_id: str,
    series_name: str,
    source: str,
    unit: str,
    frequency: str,
) -> pd.DataFrame:
    normalized = df.copy()
    normalized["series_id"] = series_id
    normalized["series_name"] = series_name
    normalized["source"] = source
    normalized["unit"] = unit
    normalized["frequency"] = frequency
    normalized = normalized[NORMALIZED_COLUMNS]
    normalized = normalized.dropna(subset=["date", "value"]).sort_values("date").reset_index(drop=True)
    return normalized


def load_ceic_series(series_def: dict) -> tuple[pd.DataFrame, dict[str, str]]:
    raw_df, meta = fetch_ceic_series(
        str(series_def["source_key"]),
        label=series_def.get("label", ""),
        unit=series_def.get("unit", ""),
        frequency=series_def.get("frequency", ""),
    )

    if raw_df.empty:
        meta["series_id"] = series_def["series_id"]
        meta["series_name"] = meta.get("series_name") or series_def.get("label", series_def["series_id"])
        return pd.DataFrame(columns=NORMALIZED_COLUMNS), meta

    normalized = _normalize_series_frame(
        raw_df,
        series_id=series_def["series_id"],
        series_name=meta["series_name"],
        source="ceic",
        unit=meta.get("unit", ""),
        frequency=meta.get("frequency", ""),
    )
    meta["series_id"] = series_def["series_id"]
    return normalized, meta


def load_series(series_def: dict) -> tuple[pd.DataFrame, dict[str, str]]:
    source = series_def["source"]
    if source == "ceic":
        return load_ceic_series(series_def)
    raise ValueError(f"Unsupported source '{source}' for series '{series_def['series_id']}'")


def load_chart_data(series_ids: list[str]) -> tuple[pd.DataFrame, dict[str, object]]:
    frames = []
    series_meta = []
    errors = []

    for series_id in series_ids:
        if series_id not in SERIES_REGISTRY:
            errors.append(f"Unknown series id '{series_id}'.")
            continue

        series_def = SERIES_REGISTRY[series_id]
        try:
            series_df, meta = load_series(series_def)
        except Exception as exc:
            meta = {
                "series_id": series_id,
                "series_name": series_def.get("label", series_id),
                "source": series_def.get("source", ""),
                "unit": series_def.get("unit", ""),
                "frequency": series_def.get("frequency", ""),
                "freshness": "",
                "status": "error",
                "message": str(exc),
            }
            series_df = pd.DataFrame(columns=NORMALIZED_COLUMNS)

        series_meta.append(meta)

        if meta.get("status") == "error":
            errors.append(meta.get("message", f"Unable to load {series_id}."))
            continue

        if not series_df.empty:
            frames.append(series_df)

    if errors and not frames:
        return pd.DataFrame(columns=NORMALIZED_COLUMNS), {
            "unit": "",
            "frequency": "",
            "errors": errors,
            "series_meta": series_meta,
        }

    combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=NORMALIZED_COLUMNS)

    units = sorted({unit for unit in combined["unit"].dropna().unique() if str(unit).strip()})
    if len(units) > 1:
        errors.append(f"Mixed units in chart: {', '.join(units)}")
        return pd.DataFrame(columns=NORMALIZED_COLUMNS), {
            "unit": "",
            "frequency": "",
            "errors": errors,
            "series_meta": series_meta,
        }

    frequencies = [value for value in combined["frequency"].dropna().unique() if str(value).strip()]
    frequency = frequencies[0] if len(frequencies) == 1 else ""
    unit = units[0] if units else ""

    return combined, {
        "unit": unit,
        "frequency": frequency,
        "errors": errors,
        "series_meta": series_meta,
    }
