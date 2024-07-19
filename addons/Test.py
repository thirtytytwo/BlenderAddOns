from typing import Dict
import bpy
import bmesh
import math
from mathutils import *
D = bpy.data
C = bpy.context

sum_normal_dic    :Dict[Vector, Vector]
pack_normal_dic   :Dict[int, Vector]
smooth_normal_dic :Dict[int, Vector]
same_normal_dic   :Dict[Vector, list[Vector]]

sum_normal_dic    = {}
pack_normal_dic   = {}
smooth_normal_dic = {}
same_normal_dic   = {}


object = C.selected_objects
mesh = object[0].data
bm = bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.triangulate(bm, faces=bm.faces[:])

uv_layer = bm.loops.layers.uv[0]

for face in bm.faces:
    normal = face.normal
    for loop in face.loops:
        index_vector = Vector(loop.vert.co).freeze()
        
        if index_vector not in sum_normal_dic:
            sum_normal_dic[index_vector] = Vector(normal)
        else:
            sum_normal_dic[index_vector] += Vector(normal)
#得到平滑法线后转入TBN空间
for face in bm.faces:
    v0 = face.loops[0].vert.co
    v1 = face.loops[1].vert.co
    v2 = face.loops[2].vert.co
    
    uv0 = face.loops[0][uv_layer].uv
    uv1 = face.loops[1][uv_layer].uv
    uv2 = face.loops[2][uv_layer].uv
    
    edge1 = v1 - v0
    edge2 = v2 - v0
    
    deltaUV1 = uv1 - uv0
    deltaUV2 = uv2 - uv0
    
    f = 1.0 / (deltaUV1.x * deltaUV2.y - deltaUV2.x * deltaUV1.y)
    tangent = Vector((edge1 * deltaUV2.y - edge2 * deltaUV1.y) * f).normalized()
    normal = face.normal
    bitangent = normal.cross(tangent).normalized()
    tbn_matrix = Matrix((tangent, bitangent, normal)).transposed()    
    # Unity导入时会自动对顶点排序，但是不会对UV排序，所以要在这里对齐Unity
    for loop in face.loops:
        index_vector = Vector(loop.vert.co).freeze()
        
        sum_normal = sum_normal_dic[index_vector]
        sum_normal.normalize()
        
        smooth_normal = sum_normal @ tbn_matrix
        smooth_normal.normalize()
        
        smooth_normal_dic[loop.index] = smooth_normal
        print(smooth_normal)