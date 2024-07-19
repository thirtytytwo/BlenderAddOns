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

print("面", len(bm.faces))
total_loops = sum(len(face.loops) for face in bm.faces)
print("面拐", total_loops)
print("顶点", len(bm.verts))

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
    tangent = face.calc_tangent_edge_diagonal()
    normal = face.normal
    bitangent = normal.cross(tangent).normalized()
    
    tbn_matrix = Matrix((tangent, bitangent, normal)).transposed()    
    # Unity导入时会自动对顶点排序，但是不会对UV排序，所以要在这里对齐Unity
    for i in range(3):
        if i == 0:
            index_vector = Vector(face.loops[i].vert.co).freeze()
        
            sum_normal = sum_normal_dic[index_vector]
            sum_normal.normalize()
        
            smooth_normal = sum_normal @ tbn_matrix
            smooth_normal.normalize()
        
            smooth_normal_dic[face.loops[i].index] = smooth_normal
        elif i == 1:
            index_vector = Vector(face.loops[i].vert.co).freeze()
        
            sum_normal = sum_normal_dic[index_vector]
            sum_normal.normalize()
        
            smooth_normal = sum_normal @ tbn_matrix
            smooth_normal.normalize()
        
            smooth_normal_dic[face.loops[i + 1].index] = smooth_normal
        else:
            index_vector = Vector(face.loops[i].vert.co).freeze()
        
            sum_normal = sum_normal_dic[index_vector]
            sum_normal.normalize()
        
            smooth_normal = sum_normal @ tbn_matrix
            smooth_normal.normalize()
        
            smooth_normal_dic[face.loops[i - 1].index] = smooth_normal
for index, IN in smooth_normal_dic.items():
    print("切线空间", IN)