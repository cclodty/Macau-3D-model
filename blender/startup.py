"""Create the reproducible Macau Blender scene template.

Run with:
    blender --background --factory-startup --python blender/startup.py
"""

from pathlib import Path

import bpy


ROOT_COLLECTIONS = (
    "00_CONTEXT",
    "10_ARCHITECTURE",
    "20_STREET",
    "30_PROPS",
    "40_LIGHTING",
    "50_CAMERAS",
)


def clear_factory_scene() -> None:
    """Remove factory objects and collections without relying on UI selection."""
    for obj in tuple(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for collection in tuple(bpy.data.collections):
        bpy.data.collections.remove(collection)


def configure_scene() -> None:
    scene = bpy.context.scene
    units = scene.unit_settings
    units.system = "METRIC"
    units.scale_length = 1.0
    units.length_unit = "METERS"

    scene["coordinate_up"] = "+Z"
    scene["local_forward"] = "-Y"
    scene["asset_origin_architecture"] = "ground structural alignment corner"
    scene["asset_origin_prop"] = "bottom center or installation point"
    scene["delivery_transform_rule"] = "apply rotation and scale"

    for name in ROOT_COLLECTIONS:
        collection = bpy.data.collections.new(name)
        scene.collection.children.link(collection)


def add_embedded_readme() -> None:
    text = bpy.data.texts.new("README_COORDINATES.txt")
    text.write(
        "Macau asset standard\n"
        "Units: Metric, Unit Scale 1.0, meters\n"
        "Axes: +Z up, local -Y forward\n"
        "Architecture origin: ground/alignment corner\n"
        "Prop origin: bottom center/installation point\n"
        "Before export: apply rotation and scale\n"
        "Use linked asset collections for repeated objects.\n"
    )


def main() -> None:
    clear_factory_scene()
    configure_scene()
    add_embedded_readme()

    output = Path(__file__).resolve().parent / "scenes" / "Macau_Startup.blend"
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output), check_existing=False)
    print(f"Created Blender startup file: {output}")


if __name__ == "__main__":
    main()
