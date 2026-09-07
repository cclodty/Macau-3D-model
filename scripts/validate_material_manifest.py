"""Validate the portable Blender/Unreal material contract without dependencies."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_IDS = {"wall_tile", "painted_concrete", "aged_glass", "painted_metal", "asphalt", "pavement", "signage"}


def validate(document):
    errors = []
    if document.get("orm_channels") != {"r": "ambient_occlusion", "g": "roughness", "b": "metallic"}:
        errors.append("ORM must pack ambient occlusion, roughness and metallic into R, G and B")
    materials = document.get("materials", [])
    if {item.get("id") for item in materials} != REQUIRED_IDS or len(materials) != len(REQUIRED_IDS):
        errors.append("materials must contain every canonical material exactly once")
    for item in materials:
        label = item.get("id", "unknown")
        for field in ("blender_name", "unreal_master", "base_color", "roughness", "metallic", "uv_scale_m"):
            if field not in item:
                errors.append(f"{label} missing {field}")
        if not item.get("blender_name", "").startswith("M_") or not item.get("unreal_master", "").startswith("M_"):
            errors.append(f"{label} material names must use the M_ prefix")
        if len(item.get("base_color", [])) != 4:
            errors.append(f"{label} base_color must be RGBA")
        for field in ("roughness", "metallic"):
            value = item.get(field)
            if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                errors.append(f"{label} {field} must be between 0 and 1")
        uv_scale = item.get("uv_scale_m")
        if not isinstance(uv_scale, (int, float)) or isinstance(uv_scale, bool) or uv_scale <= 0:
            errors.append(f"{label} uv_scale_m must be a positive number")
    bindings = document.get("slot_bindings")
    if not isinstance(bindings, dict) or not bindings:
        errors.append("slot_bindings must be a non-empty object")
    else:
        for slot, material_id in bindings.items():
            if not slot.startswith("M_"):
                errors.append(f"slot binding {slot} must use the M_ prefix")
            if material_id not in REQUIRED_IDS:
                errors.append(f"slot binding {slot} refers to unknown material {material_id}")
    return errors


def main():
    document = json.loads((ROOT / "material_manifest.json").read_text(encoding="utf-8"))
    errors = validate(document)
    if errors:
        print("Material validation failed:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    print(f"Validated {len(document['materials'])} PBR materials (manifest {document['manifest_version']}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
