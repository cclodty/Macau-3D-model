"""Build the first recognisable Pat Tat Estate street blockout in Blender.

Dimensions are explicitly provisional until survey/photo matching is available.
Run after opening Blender with:
  blender --background --python scripts/blender_build_blockout.py -- --save build/PatTat_Blockout.blend
"""

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

from blender_architecture_setup import configure_collections, configure_scene, load_manifest
from blender_material_setup import create_materials


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site_manifest.json"


def cube(collection, name, size, location, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(bpy.data.materials[material])
    if bevel:
        modifier = obj.modifiers.new("EdgeBevel", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
    obj["accuracy"] = "ESTIMATED_AWAITING_SURVEY"
    return obj


def build_podium(collection, spec):
    cube(collection, "SM_Architecture_Podium_Shell", spec["size"], spec["location"], "M_Podium_Facade", 0.12)
    cube(collection, "SM_Architecture_Podium_Canopy", (56.0, 2.2, 0.35), (0, -15.0, 6.8), "M_Podium_Soffit", 0.08)


def build_towers(collection, towers, floor_height):
    for tower in towers:
        x, y, _ = tower["location"]
        width, depth, _ = tower["size"]
        cube(collection, f"SM_Architecture_Tower_{tower['name']}_Shell", tower["size"], tower["location"], "M_Towers_Facade", 0.08)
        # Window ribbons make floor count and facade rhythm readable at street distance.
        for floor in range(tower["floors"]):
            window_z = 10.4 + floor * floor_height
            for column in (-0.3, 0.3):
                cube(collection, f"SM_Window_{tower['name']}_{floor + 1:02d}_{column:+.1f}",
                     (width * 0.36, 0.12, 1.15), (x + width * column, y - depth / 2 - 0.07, window_z), "M_Towers_Glass")
                cube(collection, f"SM_Balcony_{tower['name']}_{floor + 1:02d}_{column:+.1f}",
                     (2.2, 1.15, 0.15), (x + width * column, y - depth / 2 - 0.62, window_z - 0.72), "M_Towers_Balcony", 0.03)


def build_rooftops(collection, towers):
    for tower in towers:
        x, y, z = tower["location"]
        roof_z = z + tower["size"][2] / 2
        cube(collection, f"SM_Rooftop_{tower['name']}_Plant", (6.5, 7.0, 3.0), (x, y, roof_z + 1.5), "M_Rooftop_Concrete", 0.08)
        cube(collection, f"SM_Rooftop_{tower['name']}_Tank", (3.0, 3.0, 2.2), (x + 2.0, y, roof_z + 4.1), "M_Rooftop_Metal", 0.15)


def build_frontage(entrances, shops, facade_y, shop_count):
    spacing = 5.3
    start = -(shop_count - 1) * spacing / 2
    entrance_positions = {-16.0, 0.0, 16.0}
    for index in range(shop_count):
        x = start + index * spacing
        cube(shops, f"SM_Shop_{index + 1:02d}_Frame", (4.7, 0.35, 3.9), (x, facade_y, 2.45), "M_Shops_Frame", 0.05)
        cube(shops, f"SM_Shop_{index + 1:02d}_Glass", (4.15, 0.12, 2.65), (x, facade_y - 0.2, 2.05), "M_Shops_Glass")
        cube(shops, f"SM_Shop_{index + 1:02d}_Sign", (4.4, 0.22, 0.72), (x, facade_y - 0.28, 4.25), "M_Shops_Signage", 0.04)
    for index, x in enumerate(sorted(entrance_positions), 1):
        cube(entrances, f"SM_Entrance_{index:02d}_Portal", (3.0, 0.65, 4.4), (x, facade_y - 0.45, 2.5), "M_Entrance_Cladding", 0.08)
        cube(entrances, f"SM_Entrance_{index:02d}_Door", (2.2, 0.12, 3.35), (x, facade_y - 0.82, 2.05), "M_Entrance_Glass")


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def build_context(site):
    root = bpy.data.collections.get("CONTEXT_SITE") or bpy.data.collections.new("CONTEXT_SITE")
    if root.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(root)
    for obj in list(root.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    street = site["street"]
    cube(root, "SM_MouLaSi_Road_Blockout", street["road_size"], street["road_location"], "M_Asphalt")
    cube(root, "SM_MouLaSi_Pavement_Blockout", street["pavement_size"], street["pavement_location"], "M_Pavement")
    for x in range(-40, 41, 8):
        cube(root, f"SM_RoadMark_{x:+03d}", (4.0, 0.16, 0.025), (x, -25.0, 0.02), "M_PaintedConcrete")
    for camera_spec in site["review_cameras"]:
        data = bpy.data.cameras.get(camera_spec["name"]) or bpy.data.cameras.new(camera_spec["name"])
        camera = bpy.data.objects.get(camera_spec["name"]) or bpy.data.objects.new(camera_spec["name"], data)
        if camera.name not in root.objects:
            root.objects.link(camera)
        camera.location = camera_spec["location"]
        data.lens = camera_spec["lens_mm"]
        look_at(camera, camera_spec["target"])
    bpy.context.scene.camera = bpy.data.objects[site["review_cameras"][0]["name"]]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", type=Path, default=Path("build/PatTat_Blockout.blend"))
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(values)


def main():
    args = parse_args()
    site = json.loads(SITE.read_text(encoding="utf-8"))
    architecture = load_manifest()
    create_materials()
    configure_scene(architecture)
    collections = {
        module["id"]: collection
        for collection, module in configure_collections(architecture, False)
    }
    building = site["building"]
    build_podium(collections["Architecture_Podium"], building["podium"])
    build_towers(collections["Architecture_Towers"], building["towers"], building["floor_height"])
    build_rooftops(collections["Architecture_Rooftop"], building["towers"])
    build_frontage(collections["Architecture_Entrances"], collections["Architecture_Shops"], building["facade_y"], building["shop_count"])
    build_context(site)
    save_path = args.save if args.save.is_absolute() else ROOT / args.save
    save_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(save_path))


if __name__ == "__main__":
    main()
