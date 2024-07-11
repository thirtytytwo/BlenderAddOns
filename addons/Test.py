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
    v0 = Vector(face.loops[0].vert.co)
    v1 = Vector(face.loops[1].vert.co)
    v2 = Vector(face.loops[2].vert.co)
    
    uv0 = Vector(face.loops[0][uv_layer].uv)    
    uv1 = Vector(face.loops[1][uv_layer].uv)
    uv2 = Vector(face.loops[2][uv_layer].uv)

    
    # print(v0, v1, v2)
    # print(uv0, uv1, uv2)
    
    edge1 = v1 - v0
    edge2 = v2 - v0
    
    delta_uv1 = uv1 - uv0
    delta_uv2 = uv2 - uv0
    
    normal = face.normal
    x = normal.x
    y = normal.y
    z = normal.z
    
    if (x * x + z * z) == 0:
        continue
    tangent = Vector((x * y / math.sqrt(x * x + z * z), math.sqrt(x * x + z * z), z * y / math.sqrt(x * x + z * z)))
    bitangent = normal.cross(tangent)
    # print(tangent, bitangent, normal)
    tbn_matrix = Matrix((tangent, bitangent, normal))
    print(tbn_matrix @ normal)

# vec1 = Vector((0,1,0,0))  
# vec2 = Vector((0,1,0,0))

# vec3 = Vector((0,0,1,0))
# vec4 = Vector((0,0,0,0))

# matrix = Matrix((vec1, vec2, vec3))
# vec = Vector((1,2,0,0))
# print(matrix @ vec)