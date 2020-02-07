import bpy
import bpy_extras
import mathutils
import math
import bmesh

ROTATE_X_90 = mathutils.Quaternion((1.0, 0.0, 0.0), math.radians(90.0))

def unity_vector_to_blender(x, y, z):
    return (float(x), float(z), float(y))

def unity_quaternion_to_blender(w, x, y, z):
    return ROTATE_X_90 @ mathutils.Quaternion((-float(w), float(x), float(y), -float(z)))

def import_ar_recording(context, filepath, *args, **kwargs):
    scene = context.scene
    fps = scene.render.fps
    cam = scene.camera
    cam.rotation_mode = 'QUATERNION'

    cloud_points = { }
    planes = { }

    start_time = None
    point_cloud_mesh = bpy.data.meshes.new("cloud")
    point_cloud_obj = bpy.data.objects.new("PointCloud", point_cloud_mesh)
    scene.collection.objects.link(point_cloud_obj)
    point_cloud_mesh = point_cloud_obj.data
    point_cloud_bmesh = bmesh.new()

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
                scene.frame_current = frame

            if words[0] == 'c':
                cam.location = unity_vector_to_blender(words[1], words[2], words[3])
                q = unity_quaternion_to_blender(words[7], words[4], words[5], words[6])
                cam.rotation_quaternion = q
                cam.keyframe_insert('location')
                cam.keyframe_insert('rotation_quaternion')

            if words[0] == 'd':
                id = int(words[1])
                confidence = float(words[5])
                if confidence >= 0.5:
                    if not id in cloud_points:
                        v = unity_vector_to_blender(words[2], words[3], words[4])
                        cloud_points[id] = point_cloud_bmesh.verts.new(v)
                    else:
                        vert = cloud_points[id]
                        vert.co = unity_vector_to_blender(words[2], words[3], words[4])

            if words[0] == 'p':
                id = words[1]
                if not id in planes:
                    bpy.ops.mesh.primitive_plane_add()
                    plane = context.object
                    plane.rotation_mode = 'QUATERNION'
                    planes[id] = plane
                else:
                    plane = planes[id]
                    prev_frame = scene.frame_current - 1
                    plane.keyframe_insert('location', frame=prev_frame)
                    plane.keyframe_insert('rotation_quaternion', frame=prev_frame)
                plane.location = unity_vector_to_blender(words[2], words[3], words[4])
                q = unity_quaternion_to_blender(words[8], words[5], words[6], words[7])
                plane.rotation_quaternion = q @ ROTATE_X_90
                plane.keyframe_insert('location')
                plane.keyframe_insert('rotation_quaternion')

    point_cloud_bmesh.to_mesh(point_cloud_mesh)
    point_cloud_bmesh.free()
    
    return {'FINISHED'}


class ImportARRecording(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "import_anim.ar"
    bl_label = "Import AR Recording"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = ".txt"
    filter_glob: bpy.props.StringProperty(default="*.txt", options={'HIDDEN'})
    
    def execute(self, context):
        keywords = self.as_keywords()
        return import_ar_recording(context, **keywords)

    def draw(self, context):
        pass


def register():
    bpy.utils.register_class(ImportARRecording)

def unregister():
    bpy.utils.unregister_class(ImportARRecording)


if __name__ == "__main__":
    register()
