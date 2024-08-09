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
    packNormalDic   :Dict[int, Vector]
    smoothNormalDic :Dict[int, Vector]
    keyDic          :Dict[Vector, list[tuple[Vector, Vector]]]  

    def CleanContainers(self):
        self.sumNormalDic.clear()
        self.packNormalDic.clear()
        self.smoothNormalDic.clear()
        self.keyDic.clear()
    
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
        mesh.free_tangents()
        mesh.calc_normals_split()
        mesh.update()
        mesh.calc_tangents(uvmap='UVSet0')
        
        for loop in mesh.loops:
            indexVec = Vector(mesh.vertices[loop.vertex_index].co).freeze()
            normal = loop.normal
            
            if indexVec not in self.sumNormalDic:
                self.sumNormalDic[indexVec] = Vector(normal)
            else:
                self.sumNormalDic[indexVec] += Vector(normal)
        
        for loop in mesh.loops:
            indexVec = Vector(mesh.vertices[loop.vertex_index].co).freeze()
            normal = loop.normal
            tangent = loop.tangent
            bitangent = loop.bitangent
            
            tbnMatrix = Matrix([tangent, bitangent, normal]).transposed()
            
            sumNormal = self.sumNormalDic[indexVec]
            sumNormal.normalize()
            
            smoothNormal = sumNormal @ tbnMatrix
            smoothNormal.normalize()
            
            if indexVec not in self.keyDic:
                self.keyDic[indexVec] = [(normal, smoothNormal)]
            else:
                for vals in self.keyDic[indexVec]:
                
            

            self.smoothNormalDic[loop.index] = smoothNormal
        self.OctahedronPack()

    def CustomNormalExcute(self, mesh):
        # 计算
        self.ComputeSmoothNormal(mesh)
        # 写入数据
        if "OutlineUV" not in mesh.uv_layers.keys():
            uv_layer = mesh.uv_layers.new(name = "OutlineUV")
        else:
            self.report({'WARNING'}, "OutlineUV already exists, and we rewrite it.")
            uv_layer = mesh.uv_layers["OutlineUV"]
        
        # 这里遍历不能用loop，要用三角形
        for loop in mesh.loops:
            uv_layer.uv[loop.index].vector = Vector(self.packNormalDic[loop.index])

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None

    def execute(self, context: bpy.types.Context):
        self.sumNormalDic    = {}
        self.packNormalDic   = {}
        self.smoothNormalDic = {}
        self.keyDic          = {}

        objects = context.selected_objects
        for object in objects:
            mesh = object.data
            self.CustomNormalExcute(mesh)
        
        self.CleanContainers()
        return {'FINISHED'}