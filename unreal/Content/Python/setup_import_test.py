"""Create the repeatable material and Import Test Map assets in UE 5.4.

Run from Unreal's Output Log with:
    py "<absolute path>/setup_import_test.py"
"""

import unreal


ROOT = "/Game/Macau"
MATERIALS = f"{ROOT}/Materials"
MAP = f"{ROOT}/Maps/ImportTestMap"


def ensure_directories():
    for folder in (
        "Architecture", "Street", "Props", "Materials", "Textures", "Maps", "Blueprints"
    ):
        unreal.EditorAssetLibrary.make_directory(f"{ROOT}/{folder}")


def expression(material, cls, x, y):
    return unreal.MaterialEditingLibrary.create_material_expression(material, cls, x, y)


def texture_parameter(material, name, x, y, sampler_type):
    node = expression(material, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
    node.set_editor_property("parameter_name", name)
    node.set_editor_property("sampler_type", sampler_type)
    return node


def new_material(name):
    path = f"{MATERIALS}/{name}"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    factory = unreal.MaterialFactoryNew()
    return unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, MATERIALS, unreal.Material, factory)


def connect_texture_set(material, include_emissive=True):
    bc = texture_parameter(material, "BC", -700, -300, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    normal = texture_parameter(material, "N", -700, 0, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    orm = texture_parameter(material, "ORM", -700, 300, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    unreal.MaterialEditingLibrary.connect_material_property(bc, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    unreal.MaterialEditingLibrary.connect_material_property(normal, "RGB", unreal.MaterialProperty.MP_NORMAL)
    unreal.MaterialEditingLibrary.connect_material_property(orm, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
    unreal.MaterialEditingLibrary.connect_material_property(orm, "G", unreal.MaterialProperty.MP_ROUGHNESS)
    unreal.MaterialEditingLibrary.connect_material_property(orm, "B", unreal.MaterialProperty.MP_METALLIC)
    if include_emissive:
        emissive = texture_parameter(material, "E", -700, 550, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
        unreal.MaterialEditingLibrary.connect_material_property(emissive, "RGB", unreal.MaterialProperty.MP_EMISSIVE_COLOR)


def create_materials():
    exterior = new_material("M_Exterior_Master")
    connect_texture_set(exterior)
    unreal.MaterialEditingLibrary.recompile_material(exterior)

    road = new_material("M_Road_Master")
    connect_texture_set(road, include_emissive=False)
    unreal.MaterialEditingLibrary.recompile_material(road)

    glass = new_material("M_Glass_Master")
    glass.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    glass.set_editor_property("two_sided", True)
    tint = expression(glass, unreal.MaterialExpressionVectorParameter, -450, -100)
    tint.set_editor_property("parameter_name", "Tint")
    tint.set_editor_property("default_value", unreal.LinearColor(0.72, 0.88, 0.92, 1.0))
    opacity = expression(glass, unreal.MaterialExpressionScalarParameter, -450, 150)
    opacity.set_editor_property("parameter_name", "Opacity")
    opacity.set_editor_property("default_value", 0.25)
    roughness = expression(glass, unreal.MaterialExpressionScalarParameter, -450, 300)
    roughness.set_editor_property("parameter_name", "Roughness")
    roughness.set_editor_property("default_value", 0.08)
    unreal.MaterialEditingLibrary.connect_material_property(tint, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    unreal.MaterialEditingLibrary.connect_material_property(opacity, "", unreal.MaterialProperty.MP_OPACITY)
    unreal.MaterialEditingLibrary.connect_material_property(roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)
    unreal.MaterialEditingLibrary.recompile_material(glass)

    gray = new_material("M_GrayCard_18Percent")
    gray_value = expression(gray, unreal.MaterialExpressionConstant3Vector, -300, 0)
    # 18% linear reflectance; never use this card with automatic exposure for comparisons.
    gray_value.set_editor_property("constant", unreal.LinearColor(0.18, 0.18, 0.18, 1.0))
    unreal.MaterialEditingLibrary.connect_material_property(
        gray_value, "", unreal.MaterialProperty.MP_BASE_COLOR
    )
    unreal.MaterialEditingLibrary.recompile_material(gray)
    unreal.EditorAssetLibrary.save_directory(MATERIALS, only_if_is_dirty=False, recursive=True)


def spawn(actor_class, location, label):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(actor_class, location)
    actor.set_actor_label(label)
    return actor


def create_test_map():
    unreal.EditorLevelLibrary.new_level(MAP)
    cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")

    # 10 one-metre ruler blocks: UE uses centimetres (100 uu = 1 m).
    for index in range(10):
        marker = unreal.EditorLevelLibrary.spawn_actor_from_object(
            cube, unreal.Vector(index * 100.0, 0.0, 5.0)
        )
        marker.set_actor_label(f"Ruler_{index:02d}_1m")
        marker.set_actor_scale3d(unreal.Vector(0.98, 0.1, 0.1))

    gray_card = unreal.EditorLevelLibrary.spawn_actor_from_object(cube, unreal.Vector(450, 250, 100))
    gray_card.set_actor_label("GrayCard_18Percent")
    gray_card.set_actor_scale3d(unreal.Vector(0.02, 1.0, 1.0))
    gray_card.static_mesh_component.set_material(0, unreal.load_asset(f"{MATERIALS}/M_GrayCard_18Percent"))

    sun = spawn(unreal.DirectionalLight, unreal.Vector(0, 0, 500), "Standard_DirectionalLight")
    sun.set_actor_rotation(unreal.Rotator(-35, -45, 0), False)
    sun.get_component_by_class(unreal.DirectionalLightComponent).set_editor_property("intensity", 100000.0)
    spawn(unreal.SkyLight, unreal.Vector(0, 0, 300), "Standard_SkyLight")

    camera = spawn(unreal.CineCameraActor, unreal.Vector(-700, -900, 550), "Test_Camera")
    camera.set_actor_rotation(unreal.Rotator(-15, 38, 0), False)
    camera.get_cine_camera_component().set_editor_property("current_focal_length", 35.0)

    world = unreal.EditorLevelLibrary.get_editor_world()
    settings = world.get_world_settings()
    settings.set_editor_property("force_no_precomputed_lighting", True)
    unreal.EditorLevelLibrary.save_current_level()


def main():
    ensure_directories()
    create_materials()
    create_test_map()
    unreal.log("Macau import test assets created and saved.")


if __name__ == "__main__":
    main()
