"""Create the architecture collection contract, optional greyboxes, and FBX exports.

Run with Blender, for example:
  blender --background --python scripts/blender_architecture_setup.py -- --greybox --export-dir build/fbx --save build/architecture-greybox.blend
"""

import argparse
import json
import sys
from pathlib import Path

import bpy

from blender_material_setup import create_materials


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "architecture_manifest.json"
EXPORT_ROOT = "EXPORT_ARCHITECTURE"

# Dimensions and centres are metres and deliberately simple pipeline-test geometry.
GREYBOXES = {
    "Architecture_Podium": ((48.0, 34.0, 10.0), (0.0, 0.0, 5.0)),
    "Architecture_Towers": ((18.0, 18.0, 58.0), (-8.0, 0.0, 39.0)),
    "Architecture_Rooftop": ((9.0, 8.0, 4.0), (-8.0, 0.0, 70.0)),
    "Architecture_Entrances": ((7.0, 1.5, 4.0), (0.0, -17.0, 2.0)),
    "Architecture_Shops": ((28.0, 1.2, 4.5), (7.0, -17.2, 2.25)),
}


def load_manifest():
    with MANIFEST_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def ensure_collection(name, parent):
    collection = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    # Keep every module directly beneath the single export root.
    for owner in list(collection.users_collection):
        owner.children.unlink(collection)
    for scene in bpy.data.scenes:
        if collection.name in scene.collection.children:
            scene.collection.children.unlink(collection)
    if collection.name not in parent.children:
        parent.children.link(collection)
    return collection


def clear_collection(collection):
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def create_cube(collection, name, dimensions, location):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)
    obj["pipeline_role"] = "GREYBOX"
    return obj


def create_greybox(collection, module):
    dimensions, location = GREYBOXES[module["id"]]
    mesh = create_cube(collection, module["unreal_asset_name"] + "_GREYBOX", dimensions, location)
    for slot in module["expected_material_slots"]:
        mesh.data.materials.append(bpy.data.materials[slot])

    if module["collision"]["included"]:
        collision = create_cube(
            collection,
            "UCX_" + module["unreal_asset_name"] + "_00",
            dimensions,
            location,
        )
        collision.display_type = "WIRE"
        collision.hide_render = True
        collision["pipeline_role"] = "COLLISION"


def configure_scene(manifest):
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene.unit_settings.scale_length = 1.0
    scene["architecture_manifest_version"] = manifest["manifest_version"]
    scene["coordinate_contract"] = manifest["source_of_truth"]["coordinate_system"]
    scene["object_name_template"] = "SM_<Module>_<Descriptor>[_NN]"
    scene["collision_name_template"] = "UCX_<StaticMeshName>_NN"


def configure_collections(manifest, with_greybox):
    scene_root = bpy.context.scene.collection
    root = bpy.data.collections.get(EXPORT_ROOT) or bpy.data.collections.new(EXPORT_ROOT)
    if root.name not in scene_root.children:
        scene_root.children.link(root)
    root["export_only_children"] = True

    configured = []
    for module in manifest["modules"]:
        collection = ensure_collection(module["blender_collection"], root)
        clear_collection(collection)
        collection["module_id"] = module["id"]
        collection["unreal_asset_name"] = module["unreal_asset_name"]
        collection["unreal_content_path"] = module["unreal_content_path"]
        collection["fbx_filename"] = module["fbx_filename"]
        collection["pivot_rule"] = module["pivot_rule"]
        collection["collision_included"] = module["collision"]["included"]
        collection["material_slots_json"] = json.dumps(module["expected_material_slots"])
        collection["nanite_candidate"] = module["nanite_candidate"]
        collection["completion_status"] = module["completion_status"]
        collection["binary_asset_uri"] = module["binary_asset"]["external_uri"]
        if with_greybox:
            create_greybox(collection, module)
        configured.append((collection, module))
    return configured


def export_fbx(configured, export_dir):
    export_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for collection, module in configured:
        objects = [obj for obj in collection.all_objects if obj.type == "MESH"]
        if not objects:
            print("Skipping empty collection: " + collection.name)
            continue
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        bpy.ops.export_scene.fbx(
            filepath=str(export_dir / module["fbx_filename"]),
            use_selection=True,
            object_types={"MESH"},
            axis_forward="-Y",
            axis_up="Z",
            apply_unit_scale=True,
            bake_space_transform=False,
            add_leaf_bones=False,
        )
        bpy.ops.object.select_all(action="DESELECT")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--greybox", action="store_true", help="Populate test geometry; collections are empty otherwise.")
    parser.add_argument("--export-dir", type=Path, help="Export one FBX per non-empty module collection.")
    parser.add_argument("--save", type=Path, help="Save the generated working .blend to this path.")
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def main():
    args = parse_args()
    manifest = load_manifest()
    create_materials()
    configure_scene(manifest)
    configured = configure_collections(manifest, args.greybox)
    if args.export_dir:
        export_fbx(configured, (REPO_ROOT / args.export_dir).resolve() if not args.export_dir.is_absolute() else args.export_dir)
    if args.save:
        save_path = (REPO_ROOT / args.save).resolve() if not args.save.is_absolute() else args.save
        save_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(save_path))


if __name__ == "__main__":
    main()
