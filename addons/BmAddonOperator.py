import bmesh
import bpy
import math
from typing import Dict
from mathutils import Vector, Matrix
from collections import defaultdict


# This Example Operator will scale up the selected object
# 需要抛弃Loop的结构，改用三角面结构，结合Loop对应uv数据的hashmap结构
class ComputeOutlineNormalOperator(bpy.types.Operator):
    '''Compute Outline Normal'''
    bl_idname = "object.compute_outline_normal"
    bl_label = "ComputeOutlineNormalOperator"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    sumNormalDic    :Dict[Vector, Vector]
    sameNormalDic   :Dict[Vector, list[Vector]]
    packNormalDic   :Dict[int, Vector]
    smoothNormalDic :Dict[int, Vector]

    def CleanContainers(self):
        self.sumNormalDic.clear()
        self.packNormalDic.clear()
        self.smoothNormalDic.clear()
        self.sameNormalDic.clear()
    
    def OctahedronPack(self):
        for index, IN in self.smoothNormalDic.items():
            IN = Vector(IN).normalized()
            sum_xyz = (math.fabs(IN.x) + math.fabs(IN.y) + math.fabs(IN.z))
            
            u = IN.x / sum_xyz
            v = IN.y / sum_xyz
            w = IN.z / sum_xyz

            if w < 0.0:
                result = Vector(((1 - math.fabs(v)) * (1 if u >= 0 else -1), (1 - math.fabs(u)) * (1 if v >= 0 else -1)))
            else:
                result = Vector((u, v))
            result = Vector(((result.x * 0.5 + 0.5), (result.y * 0.5 + 0.5)))
            self.packNormalDic[index] = Vector(result)
            
    def ComputeSmoothNormal(self, mesh):
        #检查UV
        if not mesh.loops.layers.uv[0]:
            self.report({'ERROR'}, "No active UV")
            return {'CANCELED'}
        uv_layer = mesh.loops.layers.uv[0]
        for face in mesh.faces:
            normal = Vector(face.normal)
            for loop in face.loops:
                vertex = Vector(loop.vert.co).freeze()
                
                if vertex in self.sumNormalDic:
                    flag = False
                    for sameNormal in self.sameNormalDic[vertex]:
                        if sameNormal.angle(normal) < 0.01:
                            flag = True
                            break
                    if flag:
                        continue
                    else:
                        self.sameNormalDic[vertex].append(normal)
                        self.sumNormalDic[vertex] += Vector(normal)
                else:
                    self.sumNormalDic[vertex] = Vector(normal)
                    self.sameNormalDic[vertex] = [normal]
        
        for face in mesh.faces:
            for edge in face.edges:
                for loop in edge.link_loops:
                    vertex = Vector(loop.vert.co).freeze()
                    
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
                    normal = Vector(loop.vert.normal).normalized()
                    bitangent = normal.cross(tangent).normalized()
                    tbnMatrix = Matrix([tangent, bitangent, normal]).transposed()
                    
                    sumNormal = self.sumNormalDic[vertex]
                    sumNormal.normalize()
                    smoothNormal = sumNormal @ tbnMatrix
                    smoothNormal.normalize()
                    
                    self.smoothNormalDic[loop.vert.index] = smoothNormal
        self.OctahedronPack()

    def CustomNormalExcute(self, mesh):
        bm = bmesh.new()
        bm.from_mesh(mesh)
        
        #计算
        self.ComputeSmoothNormal(bm)
        
        #写入数据
        if "UVSet3" not in bm.loops.layers.uv:
            bm.loops.layers.uv.new("UVSet3")
        else:
            self.report({'WARNING'}, "UVSet3 already exists, and we rewrite it.")
        uv_layer = bm.loops.layers.uv["UVSet3"]
        
        for face in bm.faces:
            for edge in face.edges:
                for loop in edge.link_loops:
                    loop[uv_layer].uv = self.packNormalDic[loop.vert.index]
        #传回网格
        bm.to_mesh(mesh)
        bm.free()
        
    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None

    def execute(self, context: bpy.types.Context):
        self.sumNormalDic    = {}
        self.packNormalDic   = {}
        self.smoothNormalDic = {}
        self.sameNormalDic   = {}

        objects = context.selected_objects
        for object in objects:
            mesh = object.data
            self.CustomNormalExcute(mesh)
        
        self.CleanContainers()
        return {'FINISHED'}