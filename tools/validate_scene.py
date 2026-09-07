#!/usr/bin/env python3
"""Validate asset references, transforms, IDs, and deterministic placement."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
scene = json.loads((ROOT / "scenes/macau_street_layout.json").read_text())
assert scene["units"] == "metres"
assert scene["traffic_side"] == "left"
assert "random" not in scene["placement_method"]
ids = [item["id"] for item in scene["instances"]]
assert len(ids) == len(set(ids)), "instance IDs must be unique"
for item in scene["instances"]:
    path = ROOT / item["asset"]
    assert path.is_file(), f"missing asset: {path}"
    assert len(item["position"]) == len(item["rotation"]) == len(item["scale"]) == 3
    assert all(math.isfinite(v) for key in ("position", "rotation", "scale") for v in item[key])
    assert item["curb_offset"] >= 0
    assert item["note"].strip()
objs = list((ROOT / "assets").glob("**/*.obj"))
assert len(objs) >= 30, "expected complete modular asset set"
for obj in objs:
    text = obj.read_text()
    assert "mtllib ../materials.mtl" in text
    assert "\nv " in text and "\nf " in text
print(f"Validated {len(objs)} assets and {len(ids)} placed instances")
