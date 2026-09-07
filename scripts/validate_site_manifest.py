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
    for name, value in (("floor_height", building.get("floor_height")),):
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
            errors.append(f"{name} must be a positive number")
    if len(site.get("review_cameras", [])) < 3:
        errors.append("at least three review cameras are required")
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
