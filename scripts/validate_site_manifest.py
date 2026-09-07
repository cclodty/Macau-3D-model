"""Validate the provisional model dimensions without Blender."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(site):
    errors = []
    if site.get("accuracy") != "ESTIMATED_AWAITING_SURVEY":
        errors.append("blockout must remain marked ESTIMATED_AWAITING_SURVEY")
    building = site.get("building", {})
    towers = building.get("towers", [])
    if len(towers) != 3 or len({tower.get("name") for tower in towers}) != 3:
        errors.append("exactly three uniquely named tower blockouts are required")
    if building.get("shop_count", 0) < 1:
        errors.append("shop_count must be positive")
    detail = building.get("facade_detail", {})
    if not isinstance(detail.get("air_conditioners_per_floor"), int) or detail.get("air_conditioners_per_floor", 0) < 1:
        errors.append("air_conditioners_per_floor must be a positive integer")
    if not isinstance(detail.get("podium_column_count"), int) or detail.get("podium_column_count", 0) < 2:
        errors.append("podium_column_count must be an integer of at least two")
    if not detail.get("service_pipe_offsets"):
        errors.append("at least one service pipe offset is required")
    for name, value in (("floor_height", building.get("floor_height")),):
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
            errors.append(f"{name} must be a positive number")
    if len(site.get("review_cameras", [])) < 3:
        errors.append("at least three review cameras are required")
    street = site.get("street", {})
    if not street.get("street_lights_x") or not street.get("drain_x"):
        errors.append("phase-two street lights and drains must be declared")
    return errors


def main():
    site = json.loads((ROOT / "site_manifest.json").read_text(encoding="utf-8"))
    errors = validate(site)
    if errors:
        print("Site validation failed:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    print("Validated provisional site blockout and review cameras.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
