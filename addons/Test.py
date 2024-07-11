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

uv_layer = bm.loops.layers.uv[0]
for face in bm.faces:
    normal = Vector((face.normal.x, face.normal.y, face.normal.z))
    tangent = face.calc_tangent_edge()
    bitangent = tangent.cross(normal)
    bitangent.normalize()
    
    print(tangent, bitangent, normal)
    tbn_matrix = Matrix((tangent, bitangent, normal)).transposed()
    print(normal @ tbn_matrix)

# vec1 = Vector((0,1,0,0))  
# vec2 = Vector((0,1,0,0))

# vec3 = Vector((0,0,1,0))
# vec4 = Vector((0,0,0,0))

# matrix = Matrix((vec1, vec2, vec3))
# vec = Vector((1,2,0,0))
# print(matrix @ vec)