"""Dependency-free semantic validation for the architecture interchange contract."""

import json
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_IDS = {
    "Architecture_Podium",
    "Architecture_Towers",
    "Architecture_Rooftop",
    "Architecture_Entrances",
    "Architecture_Shops",
}
REQUIRED = {
    "id", "blender_collection", "unreal_asset_name", "unreal_content_path",
    "coordinates", "pivot_rule", "collision", "expected_material_slots",
    "nanite_candidate", "lod_or_distant_proxy", "fbx_filename",
    "completion_status", "binary_asset",
}


def validate(document):
    errors = []
    modules = document.get("modules", [])
    ids = {item.get("id") for item in modules}
    if ids != EXPECTED_IDS or len(modules) != 5:
        errors.append("modules must contain each of the five canonical IDs exactly once")
    for index, module in enumerate(modules):
        label = module.get("id", "modules[%d]" % index)
        missing = REQUIRED - module.keys()
        if missing:
            errors.append("%s missing: %s" % (label, ", ".join(sorted(missing))))
            continue
        if module["blender_collection"] != label:
            errors.append("%s collection must match its canonical ID" % label)
        if module["unreal_asset_name"] != "SM_" + label:
            errors.append("%s Unreal asset must be SM_<module ID>" % label)
        if module["fbx_filename"] != module["unreal_asset_name"] + ".fbx":
            errors.append("%s FBX filename must match its Unreal asset" % label)
        if not module["unreal_content_path"].startswith("/Game/Macau/Architecture/"):
            errors.append("%s Unreal path is outside the approved root" % label)
        coords = module["coordinates"]
        if coords.get("location_m") != [0, 0, 0] or coords.get("scale") != [1, 1, 1]:
            errors.append("%s must use the shared origin and unit scale" % label)
        if not isinstance(module["collision"].get("included"), bool):
            errors.append("%s collision.included must be boolean" % label)
        if not module["expected_material_slots"]:
            errors.append("%s must declare at least one material slot" % label)
        binary = module["binary_asset"]
        if not binary.get("version") or not urlparse(binary.get("external_uri", "")).scheme:
            errors.append("%s must declare a binary version and external URI" % label)
    return errors


def main():
    with (ROOT / "architecture_manifest.json").open(encoding="utf-8") as handle:
        document = json.load(handle)
    errors = validate(document)
    if errors:
        print("Manifest validation failed:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    print("Validated five architecture modules (manifest %s)." % document["manifest_version"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
