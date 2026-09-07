#!/usr/bin/env python3
"""Validate material metadata, external textures, channels, dimensions, and slots."""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path

EXPECTED_CATEGORIES = {"外牆磁磚", "塗漆混凝土", "鋁窗及金屬框", "舊玻璃", "鐵閘及欄杆", "瀝青路面", "路緣石", "行人路鋪裝", "招牌和 emissive 燈箱", "潮濕、污跡及老化 overlay"}
SUFFIX = {"base_color": "_BC", "normal": "_N", "orm": "_ORM", "emissive": "_E", "mask": "_M"}


def png_info(path: Path):
    with path.open("rb") as stream:
        header = stream.read(26)
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("not a PNG")
    width, height, bit_depth, color_type = struct.unpack(">IIBB", header[16:26])
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color_type, 0)
    return width, height, bit_depth, channels


def validate(manifest_path: Path, slots_path: Path, require_textures: bool):
    errors, warnings = [], []
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    root = manifest_path.parent / data["texture_root"]
    names, ids, categories = set(), set(), set()
    for m in data["materials"]:
        label = m.get("id", "<unknown>")
        categories.add(m.get("category"))
        if not re.fullmatch(r"[a-z][a-z0-9_]*", label): errors.append(f"{label}: invalid id")
        if not re.fullmatch(r"MAT_[A-Za-z0-9]+", m.get("blender_name", "")): errors.append(f"{label}: invalid Blender name")
        if not re.fullmatch(r"MI_[A-Za-z0-9]+", m.get("unreal_name", "")): errors.append(f"{label}: invalid Unreal instance name")
        if label in ids or m["blender_name"] in names: errors.append(f"{label}: duplicate id or Blender name")
        ids.add(label); names.add(m["blender_name"])
        resolution = tuple(m.get("resolution", []))
        if len(resolution) != 2 or any(v < 256 or v > 8192 or v & (v - 1) for v in resolution): errors.append(f"{label}: resolution must be power-of-two, 256..8192")
        if m.get("texel_density_px_per_m", 0) <= 0: errors.append(f"{label}: invalid texel density")
        for kind, relative in m.get("textures", {}).items():
            if relative is None: continue
            path = root / relative
            if Path(relative).stem.endswith(SUFFIX[kind]) is False: errors.append(f"{label}: {kind} lacks Unreal suffix {SUFFIX[kind]}")
            if m["color_space"].get(kind) != ("sRGB" if kind in ("base_color", "emissive") else "linear"): errors.append(f"{label}: wrong {kind} color space")
            if not path.is_file():
                (errors if require_textures else warnings).append(f"{label}: missing external texture {path}")
                continue
            try: width, height, depth, channels = png_info(path)
            except ValueError as exc: errors.append(f"{label}: {path}: {exc}"); continue
            if (width, height) != resolution: errors.append(f"{label}: {kind} is {width}x{height}, expected {resolution}")
            minimum = 3 if kind in ("base_color", "normal", "orm", "emissive") else 1
            if channels < minimum or depth != 8: errors.append(f"{label}: {kind} expected >= {minimum} channels at 8 bit")
    missing_categories = EXPECTED_CATEGORIES - categories
    if missing_categories: errors.append(f"missing categories: {sorted(missing_categories)}")
    slots = json.loads(slots_path.read_text(encoding="utf-8"))
    for obj in slots.get("objects", []):
        assigned = obj.get("material_slots", [])
        if not assigned: errors.append(f"{obj.get('name')}: no material slots")
        for material in assigned:
            if material not in names: errors.append(f"{obj.get('name')}: unknown slot material {material}")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("config/material_manifest.json"))
    parser.add_argument("--slots", type=Path, default=Path("config/material_slots.json"))
    parser.add_argument("--require-textures", action="store_true", help="Fail rather than warn for external binary files")
    args = parser.parse_args()
    errors, warnings = validate(args.manifest, args.slots, args.require_textures)
    for item in warnings: print(f"WARNING: {item}")
    for item in errors: print(f"ERROR: {item}", file=sys.stderr)
    print(f"Validation finished: {len(errors)} error(s), {len(warnings)} warning(s)")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
