"""Prevent estimates from being accidentally presented as surveyed calibration."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "references" / "calibration_manifest.json"
REQUIRED_MEASUREMENTS = {
    "podium_width", "podium_depth", "podium_height", "tower_a_height",
    "tower_b_height", "tower_c_height", "floor_height", "road_width",
}
ALLOWED_CONFIDENCE = {"LOW", "MEDIUM", "HIGH"}


def validate(document):
    errors = []
    sources = document.get("sources", [])
    source_ids = {source.get("id") for source in sources}
    if None in source_ids or len(source_ids) != len(sources):
        errors.append("reference source ids must be present and unique")
    measurements = document.get("measurements", [])
    ids = {item.get("id") for item in measurements}
    if ids != REQUIRED_MEASUREMENTS or len(ids) != len(measurements):
        errors.append("calibration measurements must contain every required id exactly once")
    for item in measurements:
        label = item.get("id", "unknown")
        value = item.get("value_m")
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
            errors.append(f"{label} value_m must be a positive number")
        if item.get("confidence") not in ALLOWED_CONFIDENCE:
            errors.append(f"{label} has invalid confidence")
        if item.get("method") == "BLOCKOUT_ESTIMATE":
            if item.get("source_id") is not None or item.get("confidence") != "LOW":
                errors.append(f"{label} estimate must have no source and LOW confidence")
        elif item.get("source_id") not in source_ids:
            errors.append(f"{label} refers to an unknown source")
    status = document.get("calibration_status")
    if status == "CALIBRATED" and (not sources or any(item.get("method") == "BLOCKOUT_ESTIMATE" for item in measurements)):
        errors.append("CALIBRATED requires sources and no remaining blockout estimates")
    if status == "AWAITING_REFERENCE_MEDIA" and sources:
        errors.append("status must advance when reference sources are registered")
    return errors


def main():
    errors = validate(json.loads(PATH.read_text(encoding="utf-8")))
    if errors:
        print("Calibration validation failed:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    print("Validated calibration evidence state (awaiting reference media).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
