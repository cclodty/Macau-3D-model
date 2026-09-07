"""Build a modular Macau-inspired city block and an Unreal instance manifest.

Usage: blender --background --python scripts/build_asset_hierarchy.py -- [--output DIR]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy


ROOT_NAME = "MACAU_CITY"


def parse_args() -> argparse.Namespace:
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("build"))
    return parser.parse_args(args)


def collection(name: str, parent: bpy.types.Collection) -> bpy.types.Collection:
    result = bpy.data.collections.new(name)
    parent.children.link(result)
    return result


def material(name: str, color: tuple[float, float, float, float], metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.metallic = metallic
    mat.roughness = 0.55
    return mat


def cube_mesh(name: str, size: tuple[float, float, float]):
    sx, sy, sz = (value / 2 for value in size)
    verts = [(x * sx, y * sy, z * sz) for x, y, z in (
        (-1, -1, -1), (-1, -1, 1), (-1, 1, -1), (-1, 1, 1),
        (1, -1, -1), (1, -1, 1), (1, 1, -1), (1, 1, 1),
    )]
    faces = [(0, 4, 6, 2), (1, 3, 7, 5), (0, 1, 5, 4),
             (2, 6, 7, 3), (0, 2, 3, 1), (4, 5, 7, 6)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


def object_from_mesh(name, mesh, target, location, mat, role, band, mode="STATIC_MESH"):
    obj = bpy.data.objects.new(name, mesh)
    target.objects.link(obj)
    obj.location = location
    obj.data.materials.append(mat) if not obj.data.materials else None
    obj["asset_id"] = mesh.name
    obj["asset_role"] = role
    obj["distance_band"] = band
    obj["unreal_mode"] = mode
    return obj


def repeated(name, size, transforms, target, mat, role, band="Hero"):
    """Create linked objects: every occurrence references exactly one mesh."""
    mesh = cube_mesh(name, size)
    objects = []
    for index, (location, rotation, scale) in enumerate(transforms):
        obj = object_from_mesh(
            f"{name}_I{index:03d}", mesh, target, location, mat, role, band, "HISM"
        )
        obj.rotation_euler = rotation
        obj.scale = scale
        objects.append(obj)
    return objects


def build_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for child in list(bpy.context.scene.collection.children):
        bpy.context.scene.collection.children.unlink(child)

    root = collection(ROOT_NAME, bpy.context.scene.collection)
    hero = collection("01_HERO", root)
    buildings = collection("Buildings", hero)
    facades = collection("Facade_Modules", hero)
    props = collection("Props", hero)
    roads = collection("Roads", hero)
    context = collection("02_CONTEXT", root)
    skyline = collection("03_SKYLINE", root)

    concrete = material("M_Concrete_Warm", (0.58, 0.42, 0.30, 1))
    glass = material("M_Glass_Blue", (0.05, 0.22, 0.29, 1), 0.25)
    metal = material("M_Metal_Dark", (0.055, 0.065, 0.07, 1), 0.8)
    accent = material("M_Shop_Accent", (0.72, 0.11, 0.055, 1))
    road_mat = material("M_Asphalt", (0.035, 0.04, 0.045, 1))
    pavement = material("M_Pavement", (0.42, 0.43, 0.40, 1))
    skyline_mat = material("M_Skyline", (0.12, 0.15, 0.18, 1))

    # Independent structural sections, suitable for separate Static Mesh exports.
    for name, size, loc in (
        ("BLD_A_Podium", (22, 15, 8), (0, 0, 4)),
        ("BLD_A_Tower", (13, 10, 32), (1, 0, 24)),
        ("BLD_A_Rooftop", (7, 6, 3), (1, 0, 41.5)),
    ):
        object_from_mesh(name, cube_mesh(name, size), buildings, loc, concrete,
                         "BUILDING_SECTION", "Hero")

    windows = [((x, -7.56, z), (math.pi / 2, 0, 0), (1, 1, 1))
               for z in (4.0, 7.0, 12.0, 16.0, 20.0, 24.0, 28.0, 32.0, 36.0)
               for x in (-4.0, 0.0, 4.0)]
    repeated("FM_WindowGroup", (2.7, 0.18, 1.7), windows, facades, glass,
             "FACADE_MODULE")
    repeated("FM_Balcony", (3.5, 1.2, 0.22),
             [((-5.5, -6.0, z), (0, 0, 0), (1, 1, 1)) for z in (13, 19, 25, 31)],
             facades, metal, "FACADE_MODULE")
    repeated("FM_StorefrontFrame", (4.8, 0.35, 3.4),
             [((x, -7.7, 2.2), (0, 0, 0), (1, 1, 1)) for x in (-7.5, -2.5, 2.5, 7.5)],
             facades, accent, "FACADE_MODULE")
    repeated("FM_Canopy", (4.5, 2.0, 0.25),
             [((x, -8.4, 4.1), (0, 0, 0), (1, 1, 1)) for x in (-7, 0, 7)],
             facades, metal, "FACADE_MODULE")

    repeated("PR_AirConditioner", (1.1, 0.45, 0.75),
             [((x, 5.25, z), (0, 0, 0), (1, 1, 1)) for x in (-4, 0, 4) for z in (14, 20, 26)],
             props, metal, "PROP")
    repeated("PR_Railing", (2.8, 0.10, 0.9),
             [((-5.5, -6.6, z), (0, 0, 0), (1, 1, 1)) for z in (13.5, 19.5, 25.5, 31.5)],
             props, metal, "PROP")
    repeated("PR_LampPost", (0.22, 0.22, 4.2),
             [((x, -13, 2.1), (0, 0, 0), (1, 1, 1)) for x in (-18, -8, 8, 18)],
             props, metal, "PROP")
    repeated("PR_Bin", (0.65, 0.65, 1.0),
             [((x, -11.5, 0.5), (0, 0, 0), (1, 1, 1)) for x in (-9, 9)],
             props, accent, "PROP")

    road_specs = (
        ("RD_Intersection", (24, 24, 0.20), (0, -25, -0.1), road_mat),
        ("RD_Straight", (36, 10, 0.20), (30, -25, -0.1), road_mat),
        ("RD_Sidewalk", (36, 4, 0.30), (30, -18, 0.05), pavement),
        ("RD_Kerb", (36, 0.35, 0.45), (30, -20.1, 0.225), concrete),
    )
    for name, size, loc, mat in road_specs:
        object_from_mesh(name, cube_mesh(name, size), roads, loc, mat, "ROAD_TILE", "Hero")

    # Context has broad forms only; skyline retains silhouette and one material zone.
    for index, (loc, size) in enumerate((((34, 12, 9), (15, 11, 18)), ((-28, 13, 7), (12, 10, 14)))):
        name = f"CTX_Building_{index + 1:02d}"
        object_from_mesh(name, cube_mesh(name, size), context, loc, concrete,
                         "SIMPLIFIED_BUILDING", "Context")
    for index, (x, y, h, w) in enumerate(((-55, 45, 42, 12), (-35, 52, 55, 15),
                                           (0, 58, 38, 18), (28, 51, 48, 11), (49, 46, 32, 16))):
        name = f"SKY_Mass_{index + 1:02d}"
        object_from_mesh(name, cube_mesh(name, (w, 8, h)), skyline, (x, y, h / 2),
                         skyline_mat, "DISTANT_MASS", "Skyline")

    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.length_unit = "METERS"
    bpy.context.scene["pipeline_note"] = "Keep base meshes separate; rebuild repetitions as ISM/HISM."
    return root


def unreal_transform(obj):
    loc, rot, scale = obj.matrix_world.decompose()
    # Reflection through XZ converts Blender RH to Unreal LH. Under that basis
    # change an axial vector (the quaternion XYZ part) maps to (-X, Y, -Z).
    return {
        "location_cm": [round(loc.x * 100, 4), round(-loc.y * 100, 4), round(loc.z * 100, 4)],
        "rotation_quaternion_unreal_xyzw": [round(v, 7) for v in (-rot.x, rot.y, -rot.z, rot.w)],
        "scale": [round(scale.x, 6), round(scale.y, 6), round(scale.z, 6)],
    }


def write_manifest(root, path: Path):
    groups = {}
    static_meshes = []
    for obj in sorted(root.all_objects, key=lambda item: item.name):
        record = {"object": obj.name, "asset_id": obj["asset_id"], **unreal_transform(obj)}
        if obj["unreal_mode"] == "HISM":
            groups.setdefault(obj["asset_id"], []).append(record)
        else:
            static_meshes.append({**record, "role": obj["asset_role"], "distance_band": obj["distance_band"]})
    payload = {
        "schema_version": 1,
        "coordinate_system": "Unreal centimetres (X, -Y, Z), quaternion XYZW",
        "base_mesh_rule": "Export one base mesh for each asset_id",
        "static_meshes": static_meshes,
        "instance_groups": [{"asset_id": key, "unreal_component": "HISM", "instances": value}
                            for key, value in sorted(groups.items())],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main():
    args = parse_args()
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    root = build_scene()
    write_manifest(root, output / "instance_manifest.json")
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "macau_asset_hierarchy.blend"))
    print(f"Created {output / 'macau_asset_hierarchy.blend'}")


if __name__ == "__main__":
    main()
