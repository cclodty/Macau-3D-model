"""Dependency-free checks for the Blender scene setup contract."""

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
CONFIG = json.loads((ROOT / "config" / "scene_setup.json").read_text(encoding="utf-8"))


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    cameras = CONFIG["cameras"]
    expected = {
        "CAM_MURRAY_ROAD_PANORAMA", "CAM_PAT_TAT_FRONT", "CAM_PAT_TAT_OBLIQUE",
        "CAM_SHOPS_EYE", "CAM_ENTRANCE_EYE", "CAM_HIGH_RELATIONSHIP",
        "CAM_REFERENCE_MATCH_01",
    }
    check({item["name"] for item in cameras} == expected, "fixed camera set changed")
    check(all(item["lens_mm"] >= 35 for item in cameras), "ultra-wide camera is not allowed")
    eye = [item for item in cameras if item["name"] not in {"CAM_HIGH_RELATIONSHIP"}]
    check(all(1.6 <= item["location"][2] <= 1.75 for item in eye), "eye camera height must remain credible")
    check(CONFIG["cameras"][-1]["reference_status"] == "ALIGN_REQUIRED", "reference camera must not claim an unverified match")
    check(set(CONFIG["night_regions"]) == {"SHOP_SIGNS", "STREET_LAMPS", "RESIDENTIAL_WINDOWS", "VEHICLE_LIGHTS"}, "night lights must stay grouped")
    check(sum(map(len, CONFIG["night_regions"].values())) <= 8, "night light budget exceeded")
    day = CONFIG["looks"]["subtropical_day"]
    check(0 < day["haze_density"] <= 0.02, "haze should soften distance without hiding geometry")
    check(CONFIG["looks"]["neutral_overcast"]["world_strength"] > 0.4, "neutral shadows must remain readable")
    print("scene_setup.json: all contract checks passed")


if __name__ == "__main__":
    main()
