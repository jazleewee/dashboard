from __future__ import annotations

import argparse
import pprint
import sys
from pathlib import Path

from ceic_api_client.pyceic import Ceic

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]
SECRETS_PATH = ROOT / ".streamlit" / "secrets.toml"
SERIES_CONFIG_PATH = ROOT / "src" / "series_config.py"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.series_config import SERIES_REGISTRY


def read_secrets() -> dict:
    if not SECRETS_PATH.exists():
        raise RuntimeError(f"Secrets file not found at {SECRETS_PATH}")
    with SECRETS_PATH.open("rb") as handle:
        return tomllib.load(handle)


def read_credentials() -> tuple[str, str]:
    secrets = read_secrets()
    username = str(secrets.get("CEIC_USERNAME") or secrets.get("CEIC_EMAIL") or "").strip()
    password = str(secrets.get("CEIC_PASSWORD") or "").strip()
    if not username or not password:
        raise RuntimeError("Missing CEIC_USERNAME/CEIC_EMAIL or CEIC_PASSWORD in .streamlit/secrets.toml")
    return username, password


def extract_name(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    for attr in ("name", "label", "value"):
        nested = getattr(value, attr, None)
        if isinstance(nested, str) and nested.strip():
            return nested.strip()
    return ""


def fetch_metadata(source_key: str) -> tuple[str, str]:
    meta_result = Ceic.series_metadata(str(source_key))
    if not hasattr(meta_result, "data") or not meta_result.data:
        return "", ""

    metadata = meta_result.data[0].metadata
    unit = extract_name(getattr(metadata, "unit", None))
    frequency = extract_name(getattr(metadata, "frequency", None))
    return unit, frequency


def build_updated_registry() -> tuple[dict, list[str]]:
    updated_registry = {}
    changes: list[str] = []

    for series_id, series_def in SERIES_REGISTRY.items():
        updated_def = dict(series_def)

        if updated_def.get("source") != "ceic":
            updated_registry[series_id] = updated_def
            continue

        missing_unit = not str(updated_def.get("unit", "")).strip()
        missing_frequency = not str(updated_def.get("frequency", "")).strip()

        if missing_unit or missing_frequency:
            unit, frequency = fetch_metadata(str(updated_def["source_key"]))

            if missing_unit and unit:
                updated_def["unit"] = unit
                changes.append(f"{series_id}: unit -> {unit}")

            if missing_frequency and frequency:
                updated_def["frequency"] = frequency
                changes.append(f"{series_id}: frequency -> {frequency}")

        updated_registry[series_id] = updated_def

    return updated_registry, changes


def write_registry(updated_registry: dict) -> None:
    content = "SERIES_REGISTRY = " + pprint.pformat(updated_registry, sort_dicts=False, width=100) + "\n"
    SERIES_CONFIG_PATH.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Populate missing CEIC unit/frequency metadata in src/series_config.py"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write updates back to src/series_config.py. Without this flag, only print proposed changes.",
    )
    args = parser.parse_args()

    username, password = read_credentials()
    Ceic.login(username, password)

    updated_registry, changes = build_updated_registry()

    if not changes:
        print("No missing CEIC unit/frequency fields needed updating.")
        return 0

    print("Proposed metadata updates:")
    for change in changes:
        print(f"- {change}")

    if args.apply:
        write_registry(updated_registry)
        print(f"\nUpdated {SERIES_CONFIG_PATH}")
    else:
        print("\nDry run only. Re-run with --apply to write changes.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
