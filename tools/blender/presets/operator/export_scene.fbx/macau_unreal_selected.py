"""FBX operator preset for the Macau Blender-to-Unreal asset pipeline."""

import bpy


op = bpy.context.active_operator

# Scope: export only the deliberately selected render, socket/pivot and collision
# objects. Cameras, lights and unselected collection helpers are never emitted.
op.use_selection = True
op.object_types = {"EMPTY", "MESH"}

# Coordinate system and units. Scene units remain Metric with Unit Scale 1.0;
# Unreal's importer converts the FBX centimetre metadata to Unreal Units.
op.global_scale = 1.0
op.apply_unit_scale = True
op.apply_scale_options = "FBX_SCALE_NONE"
op.axis_forward = "-Y"
op.axis_up = "Z"
op.bake_space_transform = False
op.use_space_transform = True

# Geometry payload. Custom split normals, tangent space, UV layers and material
# slots are carried by the mesh data. Triangulation is made explicit upstream.
op.use_mesh_modifiers = True
op.use_mesh_modifiers_render = True
op.mesh_smooth_type = "OFF"
op.use_subsurf = False
op.use_mesh_edges = False
op.use_tspace = True
op.use_triangles = False

# Static-environment exports contain neither rigs nor animation.
op.add_leaf_bones = False
op.use_armature_deform_only = True
op.bake_anim = False
op.use_custom_props = False

# Keep material texture references portable without copying or embedding files.
op.path_mode = "AUTO"
op.embed_textures = False
op.batch_mode = "OFF"

