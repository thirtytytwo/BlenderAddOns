import bpy
import bmesh
import math
from mathutils import *
D = bpy.data
C = bpy.context

object = C.selected_objects
mesh = object[0].data
bm = bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.triangulate(bm, faces=bm.faces[:])

uv_layer = bm.loops.layers.uv[0]
color_layer = bm.loops.layers.color.active if bm.loops.layers.color else None
print("面", len(bm.faces))
total_loops = sum(len(face.loops) for face in bm.faces)
print("面拐", total_loops)
print("顶点", len(bm.verts))

for face in bm.faces:
    #逆序
    rever_loops = list(reversed(face.loops))
    #根据逆序算面切线
    v0 = rever_loops[0].vert.co
    v1 = rever_loops[1].vert.co
    v2 = rever_loops[2].vert.co
    
    #unity 顶点逆序，但是uv不受影响
    uv0 = rever_loops[2][uv_layer].uv
    uv1 = rever_loops[1][uv_layer].uv
    uv2 = rever_loops[0][uv_layer].uv
    
    #计算切线
    deltaPos1 = v1 - v0
    deltaPos2 = v2 - v0
    
    deltaUV1 = uv1 - uv0
    deltaUV2 = uv2 - uv0
    
    r = 1.0 / (deltaUV1.x * deltaUV2.y - deltaUV1.y * deltaUV2.x)
    tangent = Vector((deltaPos1 * deltaUV2.y - deltaPos2 * deltaUV1.y) * r)
    tangent.normalize()
    
    normal = Vector(face.normal)
    bitangent = normal.cross(tangent).normalized()
    
    
    
