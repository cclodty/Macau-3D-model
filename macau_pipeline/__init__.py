bl_info = {
    "name": "Macau Normal & Bake Pipeline",
    "author": "Macau 3D Model",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Macau Pipeline",
    "category": "Object",
}

import math
import sys
import importlib.util
from datetime import datetime, timezone
from pathlib import Path

if importlib.util.find_spec("bpy"):
    import bpy
else:
    bpy = None

from .manifest import BakeManifest, TriangulationSettings, write_manifest


TRIANGULATE_NAME = "MACAU_TRIANGULATE"
EXPORT_COLLECTION = "MACAU_EXPORT"
AUDIT_TEXT = "Macau Asset Audit"


def _selected_meshes(context):
    return [obj for obj in context.selected_objects if obj.type == "MESH"]


def _ensure_triangulate(obj):
    modifier = obj.modifiers.get(TRIANGULATE_NAME) or obj.modifiers.new(TRIANGULATE_NAME, "TRIANGULATE")
    modifier.quad_method = "FIXED"
    modifier.ngon_method = "BEAUTY"
    modifier.min_vertices = 4
    if hasattr(modifier, "keep_custom_normals"):
        modifier.keep_custom_normals = True
    while obj.modifiers[-1] != modifier:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_move_down(modifier=modifier.name)
    return modifier


def prepare_mesh(obj, sharp_angle):
    mesh = obj.data
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    edge_faces = {edge.key: [] for edge in mesh.edges}
    for polygon in mesh.polygons:
        vertices = polygon.vertices
        for index, vertex in enumerate(vertices):
            key = tuple(sorted((vertex, vertices[(index + 1) % len(vertices)])))
            edge_faces[key].append(polygon)
    for edge in mesh.edges:
        faces = edge_faces[edge.key]
        edge.use_edge_sharp = len(faces) != 2 or faces[0].normal.angle(faces[1].normal) >= sharp_angle

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if bpy.app.version < (4, 1, 0):
        mesh.use_auto_smooth = True
        mesh.auto_smooth_angle = sharp_angle

    mesh.update()
    if hasattr(mesh, "calc_normals_split"):
        mesh.calc_normals_split()
    if hasattr(mesh, "normals_split_custom_set"):
        mesh.normals_split_custom_set([loop.normal.copy() for loop in mesh.loops])
    _ensure_triangulate(obj)


def audit_mesh(obj, epsilon=1.0e-10):
    mesh = obj.data
    problems = []
    negative_axes = [axis for axis, value in zip("XYZ", obj.scale) if value < 0]
    determinant = obj.matrix_world.to_3x3().determinant()
    if negative_axes:
        problems.append(f"negative scale axes: {','.join(negative_axes)}")
    if determinant < 0:
        problems.append("mirrored transform / inverted normal handedness")
    if not getattr(mesh, "has_custom_normals", False):
        problems.append("custom normals missing")
    if obj.modifiers:
        problems.append("unapplied modifiers: " + ", ".join(mod.name for mod in obj.modifiers))

    seen_faces = set()
    overlaps = 0
    for polygon in mesh.polygons:
        signature = tuple(sorted(polygon.vertices))
        if signature in seen_faces:
            overlaps += 1
        seen_faces.add(signature)
    if overlaps:
        problems.append(f"overlapping duplicate faces: {overlaps}")

    mesh.calc_loop_triangles()
    degenerate = sum(1 for triangle in mesh.loop_triangles if triangle.area <= epsilon)
    if degenerate:
        problems.append(f"degenerate triangles: {degenerate}")
    return problems


def audit_report(objects):
    lines = ["Macau Asset Audit", "=" * 18]
    has_errors = False
    for obj in objects:
        problems = audit_mesh(obj)
        has_errors |= bool(problems)
        lines.append(f"\n{obj.name}: {'FAIL' if problems else 'PASS'}")
        lines.extend(f"  - {problem}" for problem in problems)
    return "\n".join(lines) + "\n", has_errors


if bpy:
    class MacauSettings(bpy.types.PropertyGroup):
        sharp_angle: bpy.props.FloatProperty(name="Sharp angle", subtype="ANGLE", default=math.radians(60), min=0, max=math.pi)
        low_poly: bpy.props.PointerProperty(name="Low", type=bpy.types.Object)
        high_poly: bpy.props.PointerProperty(name="High", type=bpy.types.Object)
        cage: bpy.props.PointerProperty(name="Cage", type=bpy.types.Object)
        cage_extrusion: bpy.props.FloatProperty(name="Cage extrusion", default=0.01, min=0, unit="LENGTH")
        max_ray_distance: bpy.props.FloatProperty(name="Max ray distance", default=0.02, min=0, unit="LENGTH")
        export_path: bpy.props.StringProperty(name="FBX", subtype="FILE_PATH", default="//Macau_export.fbx")


    class MACAU_OT_prepare(bpy.types.Operator):
        bl_idname = "macau.prepare"
        bl_label = "Prepare Selected Meshes"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            meshes = _selected_meshes(context)
            for obj in meshes:
                prepare_mesh(obj, context.scene.macau_pipeline.sharp_angle)
            self.report({"INFO"}, f"Prepared {len(meshes)} mesh(es)")
            return {"FINISHED"}


    class MACAU_OT_manifest(bpy.types.Operator):
        bl_idname = "macau.save_manifest"
        bl_label = "Save Bake Manifest"

        def execute(self, context):
            settings = context.scene.macau_pipeline
            if not settings.low_poly or not settings.high_poly:
                self.report({"ERROR"}, "Low and High objects are required")
                return {"CANCELLED"}
            manifest = BakeManifest(
                low_poly=settings.low_poly.name,
                high_poly=settings.high_poly.name,
                cage=settings.cage.name if settings.cage else None,
                cage_extrusion=settings.cage_extrusion,
                max_ray_distance=settings.max_ray_distance,
                normal_space="TANGENT",
                triangulation=TriangulationSettings(),
                blender_version=bpy.app.version_string,
                saved_utc=datetime.now(timezone.utc).isoformat(),
            )
            context.scene["macau_bake_manifest"] = manifest.to_json()
            blend = Path(bpy.data.filepath) if bpy.data.filepath else Path.cwd() / "untitled.blend"
            path = write_manifest(manifest, blend.with_suffix(".bake.json"))
            self.report({"INFO"}, f"Saved {path}")
            return {"FINISHED"}


    class MACAU_OT_audit(bpy.types.Operator):
        bl_idname = "macau.audit"
        bl_label = "Audit Selected Meshes"

        def execute(self, context):
            report, failed = audit_report(_selected_meshes(context))
            text = bpy.data.texts.get(AUDIT_TEXT) or bpy.data.texts.new(AUDIT_TEXT)
            text.clear()
            text.write(report)
            print(report)
            self.report({"ERROR" if failed else "INFO"}, "Audit failed; see Text Editor" if failed else "Audit passed")
            return {"FINISHED"}


    class MACAU_OT_export(bpy.types.Operator):
        bl_idname = "macau.export_fbx"
        bl_label = "Freeze Triangulation & Export FBX"

        def execute(self, context):
            sources = _selected_meshes(context)
            if not sources:
                self.report({"ERROR"}, "Select at least one mesh")
                return {"CANCELLED"}
            collection = bpy.data.collections.get(EXPORT_COLLECTION) or bpy.data.collections.new(EXPORT_COLLECTION)
            if collection not in context.scene.collection.children[:]:
                context.scene.collection.children.link(collection)
            bpy.ops.object.select_all(action="DESELECT")
            copies = []
            for source in sources:
                obj = source.copy()
                obj.data = source.data.copy()
                obj.name = source.name + "_EXPORT"
                collection.objects.link(obj)
                obj.select_set(True)
                context.view_layer.objects.active = obj
                for modifier in list(obj.modifiers):
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
                tri = _ensure_triangulate(obj)
                bpy.ops.object.modifier_apply(modifier=tri.name)
                copies.append(obj)
            path = bpy.path.abspath(context.scene.macau_pipeline.export_path)
            bpy.ops.export_scene.fbx(
                filepath=path,
                use_selection=True,
                object_types={"MESH"},
                apply_unit_scale=True,
                bake_space_transform=False,
                mesh_smooth_type="EDGE",
                use_mesh_modifiers=True,
                use_tspace=True,
                add_leaf_bones=False,
            )
            self.report({"INFO"}, f"Exported {len(copies)} frozen mesh(es) to {path}")
            return {"FINISHED"}


    class MACAU_PT_panel(bpy.types.Panel):
        bl_label = "Macau Pipeline"
        bl_idname = "MACAU_PT_pipeline"
        bl_space_type = "VIEW_3D"
        bl_region_type = "UI"
        bl_category = "Macau Pipeline"

        def draw(self, context):
            layout = self.layout
            settings = context.scene.macau_pipeline
            layout.prop(settings, "sharp_angle")
            layout.operator("macau.prepare")
            layout.separator()
            for prop in ("low_poly", "high_poly", "cage", "cage_extrusion", "max_ray_distance"):
                layout.prop(settings, prop)
            layout.operator("macau.save_manifest")
            layout.separator()
            layout.prop(settings, "export_path")
            layout.operator("macau.export_fbx")
            layout.operator("macau.audit")


    CLASSES = (MacauSettings, MACAU_OT_prepare, MACAU_OT_manifest, MACAU_OT_audit, MACAU_OT_export, MACAU_PT_panel)


    def register():
        for cls in CLASSES:
            bpy.utils.register_class(cls)
        bpy.types.Scene.macau_pipeline = bpy.props.PointerProperty(type=MacauSettings)


    def unregister():
        del bpy.types.Scene.macau_pipeline
        for cls in reversed(CLASSES):
            bpy.utils.unregister_class(cls)


    def _background_audit():
        report, failed = audit_report([obj for obj in bpy.data.objects if obj.type == "MESH"])
        print(report)
        raise SystemExit(1 if failed else 0)


    if __name__ == "__main__":
        register()
        if "--audit" in sys.argv:
            _background_audit()
