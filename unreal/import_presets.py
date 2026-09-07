"""Unreal Editor Python helpers for deterministic static-mesh FBX imports."""

import unreal


def _options(normal_method):
    options = unreal.FbxImportUI()
    options.import_mesh = True
    options.import_as_skeletal = False
    options.import_materials = False
    options.import_textures = False
    options.automated_import_should_detect_type = False
    options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    static = options.static_mesh_import_data
    static.import_mesh_lo_ds = False
    static.combine_meshes = False
    static.remove_degenerates = False
    static.normal_import_method = normal_method
    return options


def _import(source_filename, destination_path, destination_name, normal_method, replace_existing=False):
    task = unreal.AssetImportTask()
    task.automated = True
    task.filename = source_filename
    task.destination_path = destination_path
    task.destination_name = destination_name
    task.replace_existing = replace_existing
    task.save = True
    task.options = _options(normal_method)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if not task.imported_object_paths:
        raise RuntimeError(f"FBX import produced no assets: {source_filename}")
    return list(task.imported_object_paths)


def compare_imports(source_filename, destination_path, asset_name="SM_Macau_NormalTest"):
    """Import an explicit-normals version and an engine-recomputed comparison."""
    imported = _import(
        source_filename,
        destination_path,
        asset_name + "_ImportedNT",
        unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS,
    )
    recomputed = _import(
        source_filename,
        destination_path,
        asset_name + "_RecomputedNT",
        unreal.FBXNormalImportMethod.FBXNIM_COMPUTE_NORMALS,
    )
    return {"imported_normals_and_tangents": imported, "recomputed": recomputed}


def import_production(source_filename, destination_path, asset_name):
    """Approved production preset: preserve Blender normals, tangents, and triangles."""
    return _import(
        source_filename,
        destination_path,
        asset_name,
        unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS,
        replace_existing=True,
    )
