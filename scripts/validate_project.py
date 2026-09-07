"""Run all dependency-free repository and cross-manifest checks."""

import json
from pathlib import Path

from validate_architecture_manifest import main as validate_architecture
from validate_calibration_manifest import main as validate_calibration
from validate_material_manifest import main as validate_materials
from validate_site_manifest import main as validate_site


ROOT = Path(__file__).resolve().parents[1]


def validate_bindings():
    architecture = json.loads((ROOT / "architecture_manifest.json").read_text(encoding="utf-8"))
    materials = json.loads((ROOT / "material_manifest.json").read_text(encoding="utf-8"))
    expected = {slot for module in architecture["modules"] for slot in module["expected_material_slots"]}
    actual = set(materials.get("slot_bindings", {}))
    missing, extra = expected - actual, actual - expected
    if missing or extra:
        if missing:
            print("Missing material slot bindings: " + ", ".join(sorted(missing)))
        if extra:
            print("Unknown material slot bindings: " + ", ".join(sorted(extra)))
        return 1
    print(f"Validated {len(expected)} architecture-to-PBR material slot bindings.")
    return 0


if __name__ == "__main__":
    results = [validate_architecture(), validate_materials(), validate_site(), validate_calibration(), validate_bindings()]
    raise SystemExit(1 if any(results) else 0)
