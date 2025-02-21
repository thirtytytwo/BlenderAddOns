import bpy
import math
from typing import Dict
from mathutils import Vector, Matrix

# This Example Operator will scale up the selected object
class ComputeOutlineNormalOperator(bpy.types.Operator):
    '''Compute Outline Normal'''
    bl_idname = "object.compute_outline_normal"
    bl_label = "ComputeOutlineNormalOperator"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    sumNormalDic    :Dict[Vector, Vector]
    packNormalDic   :Dict[int, Vector]
    smoothNormalDic :Dict[int, Vector]

    def clean_containers(self):
        self.sumNormalDic.clear()
        self.packNormalDic.clear()
        self.smoothNormalDic.clear()
        
    def ortho_normalize(self, tangent, normal):
        result = Vector((tangent - (tangent.dot(normal) * normal))).normalized()
        return result
    
    def octahedron_pack(self):
        for index, IN in self.smoothNormalDic.items():
            IN = Vector(IN).normalized()
            sumXYZ = (math.fabs(IN.x) + math.fabs(IN.y) + math.fabs(IN.z))
            
            u = IN.x / sumXYZ
            v = IN.y / sumXYZ
            w = IN.z / sumXYZ

            if w < 0.0:
                result = Vector(((1 - math.fabs(v)) * (1 if u >= 0 else -1), (1 - math.fabs(u)) * (1 if v >= 0 else -1)))
            else:
                result = Vector((u, v))
            result = Vector(((result.x * 0.5 + 0.5), (result.y * 0.5 + 0.5)))
            self.packNormalDic[index] = Vector(result)
            
    def ComputSmoothNormalMesh(self, mesh):
        mesh.calc_tangents(uvmap='MainUV')
        mesh.update()
        for loop in mesh.loops:
            indexVec = Vector(mesh.vertices[loop.vertex_index].co).freeze()
            normal = loop.normal
            
            if indexVec not in self.sumNormalDic:
                self.sumNormalDic[indexVec] = Vector(normal)
            else:
                self.sumNormalDic[indexVec] += Vector(normal)
        #得到平滑法线后转入TBN空间
        for loop in mesh.loops:
            indexVec = Vector(mesh.vertices[loop.vertex_index].co).freeze()
            tangent = loop.tangent
            normal = loop.normal
            bitangent = loop.bitangent
            tbn = Matrix((tangent, bitangent, normal)).transposed()
        
            sumNormal = self.sumNormalDic[indexVec]
            sumNormal.normalize()
        
            smoothNormal = sumNormal @ tbn
            smoothNormal.normalize()

            self.smoothNormalDic[loop.index] = smoothNormal
        #八面体打包
        self.octahedron_pack()
    
    def ComputeSmoothNormalBmesh(self, bmesh):
        pass

    def OutlineNormalExecute(self, mesh):
        #计算
        self.ComputSmoothNormalMesh(mesh)
        #写入数据
        if "OutlineUV" not in mesh.uv_layers.keys():
            uvLayer = mesh.uv_layers.new(name = "OutlineUV")
        else:
            self.report({'WARNING'},"OutlineUV already exists, and we rewrite it.")
            uvLayer = mesh.uv_layers["OutlineUV"]
        
        for loop in mesh.loops:
            uvLayer.uv[loop.index].vector = Vector(self.packNormalDic[loop.index])

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None

    def execute(self, context: bpy.types.Context):
        self.sumNormalDic    = {}
        self.packNormalDic   = {}
        self.smoothNormalDic = {}

        objects = context.selected_objects
        for object in objects:
            mesh = object.data
            self.OutlineNormalExecute(mesh)
        
        self.clean_containers()
        return {'FINISHED'}