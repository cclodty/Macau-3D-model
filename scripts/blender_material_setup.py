"""Create portable Principled BSDF preview materials from material_manifest.json."""

import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]


def load_manifest():
    return json.loads((ROOT / "material_manifest.json").read_text(encoding="utf-8"))


def configure_material(name, spec):
    """Create/update one material name from a canonical material specification."""
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = spec["base_color"]
    shader.inputs["Roughness"].default_value = spec["roughness"]
    shader.inputs["Metallic"].default_value = spec["metallic"]
    material.diffuse_color = spec["base_color"]
    material["material_id"] = spec["id"]
    material["unreal_master"] = spec["unreal_master"]
    material["uv_scale_m"] = spec["uv_scale_m"]
    material["orm_channels"] = "R=AO,G=Roughness,B=Metallic"
    material["placeholder_only"] = True
    return material


def create_materials(manifest=None, include_slot_bindings=True):
    manifest = manifest or load_manifest()
    by_id = {spec["id"]: spec for spec in manifest["materials"]}
    for spec in manifest["materials"]:
        configure_material(spec["blender_name"], spec)
    if include_slot_bindings:
        for slot_name, material_id in manifest["slot_bindings"].items():
            configure_material(slot_name, by_id[material_id])
    return manifest


def main():
    manifest = create_materials()
    print(f"Created {len(manifest['materials'])} canonical PBR materials and {len(manifest['slot_bindings'])} slot bindings.")


if __name__ == "__main__":
    main()
