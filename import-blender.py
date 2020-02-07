bl_info = {
    "name": "Import AR Recording",
    "description": "Import AR tracking data files.",
    "author": "Jacob van't Hoog",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "File > Import",
    "category": "Import-Export",
    }


import bpy
import bpy_extras
import mathutils
import math
import bmesh

from bpy.props import (
    BoolProperty,
    StringProperty
    )


ROTATE_X_90 = mathutils.Quaternion((1.0, 0.0, 0.0), math.radians(90.0))

def import_ar_recording(context, report,
        filepath,
        include_camera, include_cloud, include_planes,
        include_camera_position, include_camera_rotation,
        *args, **kwargs):
    scene = context.scene
    fps = scene.render.fps
    start_time = None
    start_frame = scene.frame_current
    camera_offset_applied = False
    
    if include_camera:
        cam = context.active_object
        if not cam:
            report({'ERROR'}, "No object selected")
            return {'FINISHED'}
        if include_camera_rotation:
            cam.rotation_mode = 'QUATERNION'
        position_offset = cam.location.copy()
    else:
        position_offset = scene.cursor.location.copy()

    if include_cloud:
        point_cloud_mesh = bpy.data.meshes.new("cloud")
        point_cloud_obj = bpy.data.objects.new("PointCloud", point_cloud_mesh)
        scene.collection.objects.link(point_cloud_obj)
        point_cloud_bmesh = bmesh.new()
        cloud_points = { }

    if include_planes:
        planes = { }
        plane_mesh = None
        plane_bm = None

    def unity_vector_to_blender(x, y, z):
        return mathutils.Vector((float(x), float(z), float(y))) + position_offset

    def unity_quaternion_to_blender(w, x, y, z):
        return ROTATE_X_90 @ mathutils.Quaternion((-float(w), float(x), float(y), -float(z)))

    def complete_plane_bmesh():
        if plane_bm:
            plane_bm.faces.new(plane_bm.verts)
            plane_bm.to_mesh(plane_mesh)
            plane_bm.free()

    with open(filepath, 'r') as file:
        while True:
            line = file.readline()
            if line == '':
                break
            line = line.strip()
            words = line.split(' ')
            if len(words) == 0:
                continue

            if words[0] == 't':
                time = float(words[1])
                if start_time is None:
                    start_time = time
                time -= start_time
                frame = int(round(time * fps))
                scene.frame_current = frame + start_frame

            if words[0] == 'c':
                if not camera_offset_applied:
                    # use initial position of camera as origin
                    position_offset -= unity_vector_to_blender(words[1], words[2], words[3]) - position_offset
                    camera_offset_applied = True
                if include_camera:
                    if include_camera_position:
                        cam.location = unity_vector_to_blender(words[1], words[2], words[3])
                        cam.keyframe_insert('location')
                    if include_camera_rotation:
                        q = unity_quaternion_to_blender(words[7], words[4], words[5], words[6])
                        cam.rotation_quaternion = q
                        cam.keyframe_insert('rotation_quaternion')

            if words[0] == 'd' and include_cloud:
                id = int(words[1])
                confidence = float(words[5])
                if confidence >= 0.5:
                    if not id in cloud_points:
                        v = unity_vector_to_blender(words[2], words[3], words[4])
                        cloud_points[id] = point_cloud_bmesh.verts.new(v)
                    else:
                        vert = cloud_points[id]
                        vert.co = unity_vector_to_blender(words[2], words[3], words[4])

            if words[0] == 'p' and include_planes:
                complete_plane_bmesh()

                id = words[1]
                if not id in planes:
                    plane_mesh = bpy.data.meshes.new("plane")
                    plane = bpy.data.objects.new("Plane", plane_mesh)
                    plane.rotation_mode = 'QUATERNION'
                    scene.collection.objects.link(plane)
                    planes[id] = plane
                    plane_bm = bmesh.new()
                else:
                    plane = planes[id]
                    plane_mesh = plane.data
                    plane_bm = bmesh.new()
                    plane_bm.from_mesh(plane_mesh)
                    bmesh.ops.delete(plane_bm, geom=plane_bm.verts, context='VERTS')
                    #prev_frame = scene.frame_current - 1
                    #plane.keyframe_insert('location', frame=prev_frame)
                    #plane.keyframe_insert('rotation_quaternion', frame=prev_frame)
                plane.location = unity_vector_to_blender(words[2], words[3], words[4])
                q = unity_quaternion_to_blender(words[8], words[5], words[6], words[7])
                plane.rotation_quaternion = q @ ROTATE_X_90
                #plane.keyframe_insert('location')
                #plane.keyframe_insert('rotation_quaternion')
            
            if words[0] == 'b' and include_planes:
                plane_bm.verts.new((float(words[1]), -float(words[2]), 0.0))

    if include_cloud:
        point_cloud_bmesh.to_mesh(point_cloud_mesh)
        point_cloud_bmesh.free()
    if include_planes:
        complete_plane_bmesh()
    
    return {'FINISHED'}


class ImportARRecording(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "import_anim.ar"
    bl_label = "Import AR Recording"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    filename_ext = ".txt"
    filter_glob: StringProperty(default="*.txt", options={'HIDDEN'})

    include_camera: BoolProperty(name="Camera", default=True)
    include_cloud: BoolProperty(name="Cloud", default=False)
    include_planes: BoolProperty(name="Planes", default=False)
    
    include_camera_position: BoolProperty(name="Position", default=True)
    include_camera_rotation: BoolProperty(name="Rotation", default=True)
    
    def execute(self, context):
        keywords = self.as_keywords()
        return import_ar_recording(context, self.report, **keywords)

    def draw(self, context):
        pass


class AR_PT_import_main(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = ""
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "IMPORT_ANIM_OT_ar"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(operator, "include_camera", toggle=True)
        row.prop(operator, "include_cloud", toggle=True)
        row.prop(operator, "include_planes", toggle=True)
        
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.label(text="Camera")
        row.prop(operator, "include_camera_position", toggle=True)
        row.prop(operator, "include_camera_rotation", toggle=True)

def menu_func_import(self, context):
    self.layout.operator(ImportARRecording.bl_idname, text="AR Recording")

def register():
    bpy.utils.register_class(ImportARRecording)
    bpy.utils.register_class(AR_PT_import_main)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportARRecording)
    bpy.utils.unregister_class(AR_PT_import_main)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
