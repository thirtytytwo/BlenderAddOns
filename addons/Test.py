import bpy
import bmesh
import math
from typing import Dict
from mathutils import *

D = bpy.data
C = bpy.context

unique_normals = set()
vertex_normals: Dict[Vector, list[Vector]] = {}

for obj in C.selected_objects:
    if obj.type == 'MESH':
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        for face in bm.faces:
            for edge in face.edges:
                count = 0
                for loop in edge.link_loops:
                    unique_normals.add(Vector(loop.vert.normal).freeze())
        bm.free()
        print(len(unique_normals))
                v0 = loop.vert.co
                v1 = loop.link_loop_prev.vert.co
                v2 = loop.link_loop_next.vert.co
                uv0 = loop[uv_layer].uv
                uv1 = loop.link_loop_prev[uv_layer].uv
                uv2 = loop.link_loop_next[uv_layer].uv
                
                deltaUV0 = uv1 - uv0
                deltaUV1 = uv2 - uv0
                
                edge0 = v1 - v0
                edge1 = v2 - v0
                
                f = 1.0 / (deltaUV0.x * deltaUV1.y - deltaUV1.x * deltaUV0.y)
                tangent = Vector(f * (deltaUV1.y * edge0 - deltaUV0.y * edge1)).normalized()
                bitangent = normal.cross(tangent).normalized()
                tbnMatrix = Matrix([tangent, bitangent, normal]).transposed()
                
                sumNormal = self.sumNormalDic[vertex]
                sumNormal.normalize()
                smoothNormal = sumNormal @ tbnMatrix
                smoothNormal.normalize()
                
                self.smoothNormalDic[loop.index] = smoothNormal