"""Create repeatable Macau lighting looks and locked review cameras in Blender."""

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

PREFIX = "MACAU_"


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(Path(__file__).parents[1] / "config" / "scene_setup.json"))
    parser.add_argument("--save-as")
    return parser.parse_args(argv)


def collection(name, parent=None):
    existing = bpy.data.collections.get(name)
    if existing:
        for obj in list(existing.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        return existing
    result = bpy.data.collections.new(name)
    (parent.children if parent else bpy.context.scene.collection.children).link(result)
    return result


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def make_light(target_collection, name, kind, location, energy, color, size=1.0, target=None):
    data = bpy.data.lights.new(PREFIX + name, kind)
    data.energy = energy
    data.color = color[:3]
    if kind == "AREA":
        data.shape = "DISK"
        data.size = size
    elif kind == "POINT":
        data.shadow_soft_size = size
    obj = bpy.data.objects.new(PREFIX + name, data)
    target_collection.objects.link(obj)
    obj.location = location
    if target is not None:
        aim(obj, target)
    return obj


def make_world(name, settings, volume=False):
    old = bpy.data.worlds.get(name)
    if old:
        bpy.data.worlds.remove(old)
    world = bpy.data.worlds.new(name)
    world.use_nodes = True
    nodes = world.node_tree.nodes
    background = nodes.get("Background")
    background.inputs["Color"].default_value = settings["world_color"]
    background.inputs["Strength"].default_value = settings["world_strength"]
    if volume:
        haze = nodes.new("ShaderNodeVolumePrincipled")
        haze.name = "MACAU_HUMID_HAZE"
        haze.inputs["Density"].default_value = settings["haze_density"]
        haze.inputs["Anisotropy"].default_value = settings["haze_anisotropy"]
        haze.inputs["Color"].default_value = settings["haze_color"]
        world.node_tree.links.new(haze.outputs["Volume"], nodes["World Output"].inputs["Volume"])
    return world


def exclude_except(layer_collection, active_name):
    for child in layer_collection.children:
        if child.name.startswith("MACAU_LIGHTING_"):
            child.exclude = child.name != active_name


def make_view_layer(name, light_collection, world):
    layer = bpy.context.scene.view_layers.get(name) or bpy.context.scene.view_layers.new(name)
    exclude_except(layer.layer_collection, light_collection)
    # Blender worlds are scene-wide. Keep the intended world alongside each layer
    # as metadata; handlers/pipeline code can switch it before batch rendering.
    layer["macau_world"] = world.name
    return layer


def setup_lighting(config):
    neutral = collection("MACAU_LIGHTING_NEUTRAL")
    subtropical = collection("MACAU_LIGHTING_SUBTROPICAL")
    night = collection("MACAU_LIGHTING_NIGHT")

    n = config["looks"]["neutral_overcast"]
    make_light(neutral, "NEUTRAL_KEY", "AREA", n["key_location"], n["key_energy"], (0.94, 0.97, 1.0), n["key_size"], n["key_target"])
    make_light(neutral, "NEUTRAL_FILL", "AREA", n["fill_location"], n["fill_energy"], (0.83, 0.9, 1.0), n["fill_size"], n["fill_target"])

    day = config["looks"]["subtropical_day"]
    sun = make_light(subtropical, "SUBTROPICAL_SUN", "SUN", (0, 0, 20), day["sun_energy"], (1.0, 0.92, 0.8))
    sun.data.angle = math.radians(day["sun_angle_degrees"])
    sun.rotation_euler = [math.radians(v) for v in day["sun_rotation_degrees"]]

    for region_name, lights in config["night_regions"].items():
        region = collection(PREFIX + region_name, night)
        region["lighting_region"] = region_name
        for item in lights:
            make_light(region, item["name"], item["type"], item["location"], item["energy"], item["color"], item.get("size", item.get("radius", 1.0)), item.get("target"))

    worlds = {
        "LOOKDEV_NEUTRAL": make_world("MACAU_WORLD_NEUTRAL", n),
        "DAY_SUBTROPICAL": make_world("MACAU_WORLD_SUBTROPICAL", day, volume=True),
        "NIGHT_OPTIONAL": make_world("MACAU_WORLD_NIGHT", config["looks"]["night"]),
    }
    make_view_layer("LOOKDEV_NEUTRAL", neutral.name, worlds["LOOKDEV_NEUTRAL"])
    make_view_layer("DAY_SUBTROPICAL", subtropical.name, worlds["DAY_SUBTROPICAL"])
    make_view_layer("NIGHT_OPTIONAL", night.name, worlds["NIGHT_OPTIONAL"])
    bpy.context.scene.world = worlds["LOOKDEV_NEUTRAL"]


def setup_cameras(items):
    cameras = collection("MACAU_CAMERAS")
    for item in items:
        data = bpy.data.cameras.new(item["name"])
        data.lens = item["lens_mm"]
        data.sensor_width = 36.0
        data.show_composition_thirds = True
        data.dof.use_dof = False
        obj = bpy.data.objects.new(item["name"], data)
        cameras.objects.link(obj)
        obj.location = item["location"]
        aim(obj, item["target"])
        obj["purpose"] = item["purpose"]
        obj["fixed_review_camera"] = True
        obj["reference_status"] = item.get("reference_status", "APPROVED_BASELINE")
        obj.hide_select = True
    bpy.context.scene.camera = bpy.data.objects["CAM_MURRAY_ROAD_PANORAMA"]


def configure_render(settings):
    scene = bpy.context.scene
    scene.render.engine = settings["engine"]
    scene.render.resolution_x = settings["resolution_x"]
    scene.render.resolution_y = settings["resolution_y"]
    scene.render.resolution_percentage = settings["resolution_percentage"]
    scene.view_settings.look = "AgX - Medium High Contrast"


def main():
    args = parse_args()
    with open(args.config, encoding="utf-8") as stream:
        config = json.load(stream)
    setup_lighting(config)
    setup_cameras(config["cameras"])
    configure_render(config["render"])
    if args.save_as:
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(args.save_as).resolve()))
    print("Macau lighting and camera setup complete: neutral lookdev is active.")


if __name__ == "__main__":
    main()
