"""Build the Pak Tat San Chun (八達新邨) survey blockout in Blender.

Run with Blender 4.0 or newer::

    blender --background --python source/create_blockout.py

The script deliberately uses only Blender's bundled Python modules.  Dimensions
are in metres and all editable survey assumptions are collected near the top.
"""

import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
OUTPUT = SOURCE / "pak_tat_san_chun_master.blend"
BLOCKOUT = SOURCE / "pak_tat_san_chun_blockout.blend"

# Local survey grid. Origin = north-west kerb tangent point at the junction of
# the two modelled estate access roads. +Y is true north, +X is east, +Z is up.
BUILDINGS = [
    # name, centre x/y, podium x/y/z, tower x/y/z, tower offset x/y, roof plant
    ("八達新邨_A座", (-39, 31), (36, 28, 12), (27, 19, 54), (1, 2), (13, 7, 4)),
    ("八達新邨_B座", (0, 32), (34, 28, 12), (25, 19, 60), (0, 2), (12, 7, 4)),
    ("八達新邨_C座", (38, 31), (34, 28, 12), (25, 19, 57), (-1, 2), (12, 7, 4)),
    ("八達新邨_D座", (-35, -34), (38, 27, 10), (28, 18, 51), (1, -1), (13, 7, 4)),
    ("八達新邨_E座", (7, -34), (38, 27, 10), (28, 18, 57), (-1, -1), (13, 7, 4)),
    ("相鄰樓宇_東", (61, -34), (30, 35, 9), (23, 27, 66), (0, 0), (11, 8, 5)),
    ("相鄰樓宇_西", (-66, -24), (24, 45, 8), (18, 34, 48), (0, 1), (9, 10, 4)),
]

ROAD_GREY = (0.10, 0.11, 0.12, 1)
KERB_GREY = (0.42, 0.44, 0.46, 1)
BUILDING_GREY = (0.55, 0.57, 0.60, 1)
TOWER_GREY = (0.67, 0.69, 0.72, 1)
MARKING = (0.85, 0.85, 0.80, 1)
ANNOTATION = (0.95, 0.35, 0.08, 1)


def material(name, colour):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = colour
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = colour
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.82
    return mat


def collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def move_to(obj, col):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    col.objects.link(obj)


def box(name, centre, size, mat, col, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=(centre[0], centre[1], centre[2] + size[2] / 2))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("轉角半徑", "BEVEL")
        mod.width = bevel
        mod.segments = 4
    move_to(obj, col)
    return obj


def curve(name, points, width, mat, col, z=0.04, cyclic=False):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.bevel_depth = width / 2
    data.bevel_resolution = 2
    spline = data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, coordinate in zip(spline.points, points):
        point.co = (coordinate[0], coordinate[1], z, 1)
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, data)
    col.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def text(name, body, location, size, col, rotation=(0, 0, 0)):
    data = bpy.data.curves.new(name, "FONT")
    data.body = body
    data.align_x = "CENTER"
    data.size = size
    data.extrude = 0.025
    obj = bpy.data.objects.new(name, data)
    col.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation
    return obj


def camera(name, location, target, lens, col):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.sensor_width = 36
    obj = bpy.data.objects.new(name, data)
    col.objects.link(obj)
    obj.location = location
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    obj["用途"] = "固定驗收相機；請勿移動"
    obj["鏡頭_mm"] = lens
    return obj


def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.curves, bpy.data.meshes, bpy.data.materials, bpy.data.cameras):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)

    scene = bpy.context.scene
    scene.name = "八達新邨_灰模"
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.world.color = (0.055, 0.065, 0.08)
    scene["座標基準"] = "原點：屋苑西北側兩條出入口道路的路緣切點；+Y 真北"
    scene["精度狀態"] = "測繪灰模；所有尺寸須以現場測量/核准圖則覆核"
    scene["道路轉彎半徑_m"] = "內緣6.0；外緣12.0"

    roads = collection("01_道路中心線及車道")
    walks = collection("02_行人路_路緣_斜坡_出入口")
    footprints = collection("03_建築退界及佔地")
    masses = collection("04_裙樓_塔樓_天台")
    cameras = collection("05_固定相機")
    guides = collection("06_比例尺_北向_註記")

    mats = {
        "road": material("道路灰", ROAD_GREY), "kerb": material("路緣灰", KERB_GREY),
        "podium": material("裙樓灰", BUILDING_GREY), "tower": material("塔樓灰", TOWER_GREY),
        "line": material("道路標線", MARKING), "note": material("驗收註記", ANNOTATION),
    }

    # 7.2 m estate road crosses a 9.0 m north/south distributor. The quarter
    # circle at their junction explicitly records the 6 m inside turning radius.
    box("南北道路_9m", (0, 0, -0.15), (9, 150, 0.3), mats["road"], roads)
    box("東西道路_7.2m", (0, 0, -0.14), (150, 7.2, 0.28), mats["road"], roads)
    curve("南北道路中心線", [(0, -75), (0, 75)], 0.12, mats["line"], roads)
    curve("東西道路中心線", [(-75, 0), (75, 0)], 0.12, mats["line"], roads)
    for x in (-3.6, 3.6):
        curve(f"南北車道邊界_{x:+.1f}", [(x, -75), (x, 75)], 0.10, mats["line"], roads)
    for y in (-2.8, 2.8):
        curve(f"東西車道邊界_{y:+.1f}", [(-75, y), (75, y)], 0.10, mats["line"], roads)
    arc = [(3.6 + 6 * math.cos(math.radians(a)), 2.8 + 6 * math.sin(math.radians(a))) for a in range(180, 271, 5)]
    curve("轉角內緣_R6m", arc, 0.16, mats["note"], roads, z=0.08)

    # Footways are continuous; dropped kerbs and driveway ramps are separate,
    # shallow wedges so they remain inspectable in plan and perspective views.
    box("北側行人路", (0, 5.3, 0), (150, 3.4, 0.15), mats["kerb"], walks)
    box("南側行人路", (0, -5.3, 0), (150, 3.4, 0.15), mats["kerb"], walks)
    box("西側行人路", (-6.2, 0, 0), (3.4, 150, 0.15), mats["kerb"], walks)
    box("東側行人路", (6.2, 0, 0), (3.4, 150, 0.15), mats["kerb"], walks)
    for i, (x, y, sx, sy) in enumerate([(-24, 5.3, 6, 3.4), (26, -5.3, 7, 3.4), (6.2, 23, 3.4, 6)]):
        ramp = box(f"無障礙斜坡_{i+1}", (x, y, 0), (sx, sy, 0.15), mats["note"], walks)
        ramp.rotation_euler[1 if sx > sy else 0] = math.radians(2.8)
    for x in (-24, 26):
        curve(f"車輛出入口_{x}", [(x - 3, 6.9), (x + 3, 6.9)], 0.20, mats["note"], walks)

    for name, (x, y), podium, tower, offset, plant in BUILDINGS:
        # Dashed-style setback proxy: a closed 0.15 m orange survey boundary.
        margin = 2.0
        hx, hy = podium[0] / 2 + margin, podium[1] / 2 + margin
        curve(name + "_建築退界", [(x-hx,y-hy),(x+hx,y-hy),(x+hx,y+hy),(x-hx,y+hy)],
              0.15, mats["note"], footprints, z=0.09, cyclic=True)
        box(name + "_佔地輪廓", (x, y, 0), (podium[0], podium[1], 0.08), mats["note"], footprints)
        box(name + "_裙樓", (x, y, 0), podium, mats["podium"], masses, bevel=0.35)
        tx, ty = x + offset[0], y + offset[1]
        box(name + "_塔樓", (tx, ty, podium[2]), tower, mats["tower"], masses, bevel=0.45)
        box(name + "_天台構築物", (tx, ty, podium[2] + tower[2]), plant, mats["kerb"], masses, bevel=0.2)
        for obj_name, height in ((name + "_裙樓", podium[2]), (name + "_塔樓", podium[2] + tower[2])):
            bpy.data.objects[obj_name]["主要標高_m"] = height

    # 0–20 m checker scale and true-north arrow live outside the road envelope.
    for i in range(4):
        box(f"比例尺_{i*5}-{(i+1)*5}m", (-65 + i*5 + 2.5, 69, 0), (5, 1.2, 0.12),
            mats["line" if i % 2 else "road"], guides)
    text("比例尺文字", "0    5    10    15    20 m", (-55, 67.3, 0.15), 1.3, guides)
    curve("北向箭桿", [(67, 60), (67, 72)], 0.5, mats["note"], guides, z=0.15)
    curve("北向箭頭", [(64.5, 68), (67, 73), (69.5, 68)], 0.5, mats["note"], guides, z=0.15)
    text("北向_N", "N", (67, 75, 0.15), 2.6, guides)
    text("原點標記", "ORIGIN (0,0,0)", (13, 10, 0.2), 1.2, guides)
    curve("原點十字", [(-2, 0), (2, 0)], 0.2, mats["note"], guides, z=0.2)
    curve("原點十字_Y", [(0, -2), (0, 2)], 0.2, mats["note"], guides, z=0.2)

    fixed = [
        camera("驗收相機_01_西北街角", (-73, 64, 8), (0, 5, 24), 42, cameras),
        camera("驗收相機_02_東南街角", (73, -64, 7), (0, -5, 23), 45, cameras),
        camera("驗收相機_03_道路軸線", (0, -70, 5.2), (0, 15, 18), 50, cameras),
        camera("驗收相機_04_鳥瞰", (105, -120, 130), (0, 0, 8), 52, cameras),
    ]
    scene.camera = fixed[0]

    bpy.ops.object.light_add(type="SUN", location=(20, -30, 90))
    sun = bpy.context.object
    sun.name = "灰模日光"
    sun.rotation_euler = (math.radians(28), math.radians(-18), math.radians(28))
    sun.data.energy = 2.2
    move_to(sun, guides)

    SOURCE.mkdir(parents=True, exist_ok=True)
    # Blockout excludes only the annotation guides; master keeps everything.
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
    guides.hide_render = True
    bpy.ops.wm.save_as_mainfile(filepath=str(BLOCKOUT), copy=True)
    guides.hide_render = False
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
    print(f"Created {OUTPUT} and {BLOCKOUT}")


if __name__ == "__main__":
    main()
