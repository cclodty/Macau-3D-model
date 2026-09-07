"""Check that the delivery structure and tabular manifests are reviewable."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "deliverables/master",
    "deliverables/textures",
    "deliverables/exports",
    "deliverables/screenshots/day",
    "deliverables/assets.csv",
    "deliverables/licenses.csv",
    "deliverables/performance.md",
    "deliverables/acceptance.md",
    "deliverables/privacy-copyright-review.md",
]


def main() -> int:
    missing = [entry for entry in REQUIRED if not (ROOT / entry).exists()]
    for filename in ("assets.csv", "licenses.csv"):
        with (ROOT / "deliverables" / filename).open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
            if not rows:
                missing.append(f"deliverables/{filename}: no inventory rows")
    if missing:
        print("Delivery incomplete:")
        print("\n".join(f"- {item}" for item in missing))
        return 1
    print("Delivery structure and manifests are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

