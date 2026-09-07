"""Validate and export the open Blender scene without modifying source art.

Run through Blender, not system Python. The process deliberately fails when a
required production rule is violated so an invalid package cannot look final.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^(BLD|STR|PRP|COL)_[A-Za-z0-9_]+(?:_LOD[0-3])?$")
LOD_RE = re.compile(r"_LOD([0-3])$")


@dataclass(frozen=True)
class Finding:
    severity: str
    asset: str
    check: str
    detail: str


def parse_args() -> argparse.Namespace:
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    return parser.parse_args(args)


def close(value: float, expected: float, tolerance: float = 1e-4) -> bool:
    return abs(value - expected) <= tolerance


def validate_mesh(obj: bpy.types.Object, config: dict) -> list[Finding]:
    findings: list[Finding] = []
    add = lambda level, check, detail: findings.append(
        Finding(level, obj.name, check, detail)
    )
    if not NAME_RE.fullmatch(obj.name):
        add("ERROR", "naming", "Use PREFIX_Name_LODn; prefixes: BLD/STR/PRP/COL")
    if any(not close(v, 0.0) for v in obj.rotation_euler):
        add("ERROR", "axis", "Rotation must be applied")
    if any(not close(v, 1.0) for v in obj.scale):
        add("ERROR", "scale", "Scale must be applied")
    if obj.data and obj.data.vertices:
        bounds = [obj.data.vertices[i].co for i in range(len(obj.data.vertices))]
        if any(0.0 < min(point[axis] for point in bounds) or
               0.0 > max(point[axis] for point in bounds) for axis in range(3)):
            add("WARN", "origin", "Origin appears to be outside the mesh")
    if obj.data and len(obj.data.polygons) and not obj.data.uv_layers:
        add("ERROR", "uv", "Missing primary UV channel")
    if any(poly.normal.length < 0.99 for poly in obj.data.polygons):
        add("ERROR", "normals", "Degenerate face normal detected")
    if not obj.name.startswith("COL_") and len(obj.data.uv_layers) < 2:
        add("ERROR", "lightmap", "Missing non-overlapping lightmap UV channel")
    if obj.name.startswith("COL_") and obj.display_type != "WIRE":
        add("WARN", "collision", "Collision helper should display as wire")
    if not obj.name.startswith("COL_") and not LOD_RE.search(obj.name):
        add("ERROR", "lod", "Renderable mesh has no LOD0-LOD3 suffix")
    for material in obj.data.materials:
        if material and not any(
            material.name.endswith(s) for s in config["allowed_material_suffixes"]
        ):
            add("ERROR", "material", f"No target suffix on {material.name}")
        if material and material.use_nodes:
            importance = obj.get("importance", "prop")
            budget = config["texture_budgets"].get(importance)
            if budget is None:
                add("ERROR", "texture", f"Unknown importance category: {importance}")
                continue
            for node in material.node_tree.nodes:
                image = getattr(node, "image", None)
                if image and max(image.size) > budget:
                    add(
                        "ERROR", "texture",
                        f"{image.name} is {max(image.size)}px; {importance} budget is {budget}px",
                    )
    return findings


def validate_scene(config: dict) -> list[Finding]:
    findings: list[Finding] = []
    scene = bpy.context.scene
    if scene.unit_settings.system != "METRIC":
        findings.append(Finding("ERROR", "SCENE", "units", "Use metric units"))
    if not close(scene.unit_settings.scale_length, config["unit_scale_meters"]):
        findings.append(Finding("ERROR", "SCENE", "units", "Unexpected unit scale"))
    meshes = [obj for obj in scene.objects if obj.type == "MESH"]
    if not meshes:
        findings.append(Finding("ERROR", "SCENE", "content", "No mesh assets found"))
    for obj in meshes:
        findings.extend(validate_mesh(obj, config))
    return findings


def write_report(findings: list[Finding]) -> Path:
    output = ROOT / "deliverables" / "reports" / "validation.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["severity", "asset", "check", "detail"])
        writer.writerows((f.severity, f.asset, f.check, f.detail) for f in findings)
    return output


def export_scene(formats: list[str]) -> None:
    output = ROOT / "deliverables" / "exports"
    output.mkdir(parents=True, exist_ok=True)
    if "gltf" in formats:
        bpy.ops.export_scene.gltf(
            filepath=str(output / "macau_scene.glb"), export_format="GLB",
            export_yup=True, export_apply=True,
        )
    if "fbx" in formats:
        bpy.ops.export_scene.fbx(
            filepath=str(output / "macau_scene.fbx"), axis_forward="-Z",
            axis_up="Y", apply_unit_scale=True, use_space_transform=True,
        )


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    findings = validate_scene(config)
    report = write_report(findings)
    errors = [item for item in findings if item.severity == "ERROR"]
    print(f"Validation report: {report} ({len(errors)} errors)")
    if errors:
        return 1
    export_scene(config["exports"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
