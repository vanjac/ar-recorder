import bpy
import mathutils
import math
import bmesh

scene = bpy.context.scene
fps = scene.render.fps
cam = scene.camera
cam.rotation_mode = 'QUATERNION'

cloud_points = { }
planes = { }

plane_rotate = mathutils.Quaternion((1.0, 0.0, 0.0), math.radians(90.0))

point_cloud_mesh = bpy.data.meshes.new("cloud")
point_cloud_obj = bpy.data.objects.new("PointCloud", point_cloud_mesh)
scene.collection.objects.link(point_cloud_obj)
point_cloud_mesh = point_cloud_obj.data
point_cloud_bmesh = bmesh.new()

with open(bpy.path.abspath("//recording"), 'r') as file:
    print("Importing recording...")
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
            frame = int(time * fps)
            #print("Frame", frame)
            scene.frame_current = frame
        if words[0] == 'c':
            v = mathutils.Vector((float(words[1]), float(words[2]), -float(words[3])))
            q = mathutils.Quaternion((-float(words[7]), float(words[4]), float(words[5]), -float(words[6])))
            cam.location = v
            cam.rotation_quaternion = q
            cam.keyframe_insert('location')
            cam.keyframe_insert('rotation_quaternion')
        if words[0] == 'd':
            id = int(words[1])
            if not id in cloud_points:
                v = (float(words[2]), float(words[3]), -float(words[4]))
                cloud_points[id] = point_cloud_bmesh.verts.new(v)
            else:
                vert = cloud_points[id]
                vert.co = (float(words[2]), float(words[3]), -float(words[4]))
        if words[0] == 'p':
            id = words[1]
            v = mathutils.Vector((float(words[2]), float(words[3]), -float(words[4])))
            q = mathutils.Quaternion((-float(words[8]), float(words[5]), float(words[6]), -float(words[7])))
            if not id in planes:
                bpy.ops.mesh.primitive_plane_add()
                plane = bpy.context.object
                plane.rotation_mode = 'QUATERNION'
                planes[id] = plane
            else:
                plane = planes[id]
                prev_frame = scene.frame_current - 1
                plane.keyframe_insert('location', frame=prev_frame)
                plane.keyframe_insert('rotation_quaternion', frame=prev_frame)
            plane.location = v
            plane.rotation_quaternion = q @ plane_rotate
            plane.keyframe_insert('location')
            plane.keyframe_insert('rotation_quaternion')

point_cloud_bmesh.to_mesh(point_cloud_mesh)
point_cloud_bmesh.free()

print("Done!")
