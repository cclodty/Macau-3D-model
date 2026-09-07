#!/usr/bin/env python3
"""Build Blender Principled BSDF preview materials from the project manifest.

Run with: blender file.blend --background --python scripts/build_blender_materials.py
           -- --manifest config/material_manifest.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


SOCKETS = {"base_color": "Base Color", "roughness": "Roughness", "metallic": "Metallic"}


def arguments() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="config/material_manifest.json")
    parser.add_argument("--texture-root", help="Override the manifest-relative texture root")
    return parser.parse_args(argv)


def image_node(nodes, path: Path, color_space: str, label: str):
    if not path.is_file():
        return None
    node = nodes.new("ShaderNodeTexImage")
    node.label = label
    node.image = bpy.data.images.load(str(path.resolve()), check_existing=True)
    node.image.colorspace_settings.name = "sRGB" if color_space == "sRGB" else "Non-Color"
    return node


def placeholder(nodes, links, principled, rgba):
    """A stable procedural checker makes missing binaries obvious without pink assets."""
    checker = nodes.new("ShaderNodeTexChecker")
    checker.label = "PROCEDURAL PLACEHOLDER"
    checker.inputs["Color1"].default_value = rgba
    checker.inputs["Color2"].default_value = tuple(max(0.0, c * 0.45) for c in rgba[:3]) + (rgba[3],)
    checker.inputs["Scale"].default_value = 8.0
    links.new(checker.outputs["Color"], principled.inputs["Base Color"])


def build(entry: dict, texture_root: Path):
    material = bpy.data.materials.get(entry["blender_name"]) or bpy.data.materials.new(entry["blender_name"])
    material.use_nodes = True
    material.diffuse_color = entry["defaults"]["base_color"]
    material["manifest_id"] = entry["id"]
    material["supports_wetness"] = entry["features"]["wetness"]
    material["supports_aging_blend"] = entry["features"]["aging_blend"]
    nodes, links = material.node_tree.nodes, material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    defaults = entry["defaults"]
    bsdf.inputs["Base Color"].default_value = defaults["base_color"]
    bsdf.inputs["Roughness"].default_value = defaults["roughness"]
    bsdf.inputs["Metallic"].default_value = defaults["metallic"]

    textures, spaces = entry["textures"], entry["color_space"]
    base = image_node(nodes, texture_root / textures["base_color"], spaces["base_color"], "Base Color")
    if base:
        links.new(base.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        placeholder(nodes, links, bsdf, tuple(defaults["base_color"]))

    normal_path = textures.get("normal")
    normal = image_node(nodes, texture_root / normal_path, spaces["normal"], "Normal") if normal_path else None
    if normal:
        normal_map = nodes.new("ShaderNodeNormalMap")
        normal_map.inputs["Strength"].default_value = defaults["normal_strength"]
        links.new(normal.outputs["Color"], normal_map.inputs["Color"])
        links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])

    orm_path = textures.get("orm")
    orm = image_node(nodes, texture_root / orm_path, spaces["orm"], "ORM (R=AO G=Roughness B=Metallic)") if orm_path else None
    if orm:
        separate = nodes.new("ShaderNodeSeparateColor")
        links.new(orm.outputs["Color"], separate.inputs["Color"])
        links.new(separate.outputs["Green"], bsdf.inputs["Roughness"])
        links.new(separate.outputs["Blue"], bsdf.inputs["Metallic"])

    emissive_path = textures.get("emissive")
    emissive = image_node(nodes, texture_root / emissive_path, spaces["emissive"], "Emissive") if emissive_path else None
    emission_input = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    if emissive and emission_input:
        links.new(emissive.outputs["Color"], emission_input)
        strength = bsdf.inputs.get("Emission Strength")
        if strength:
            strength.default_value = 2.0
    return material


def main() -> None:
    args = arguments()
    manifest_path = Path(args.manifest).resolve()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    texture_root = Path(args.texture_root).resolve() if args.texture_root else manifest_path.parent / data["texture_root"]
    for entry in data["materials"]:
        build(entry, texture_root)
    print(f"Built {len(data['materials'])} preview materials; textures root: {texture_root}")


if __name__ == "__main__":
    main()
