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
    
    packNormalDic   :Dict[int, Vector]
    smoothNormalDic :Dict[int, Vector]

    def clean_containers(self): 
        self.packNormalDic.clear()
        self.smoothNormalDic.clear()
    
    def octahedron_pack(self):
        for index, IN in self.smoothNormalDic.items():
            normal = IN.normalized()
            sumXYZ = abs(IN.x) + abs(IN.y) + abs(IN.z)
            
            u = normal.x / sumXYZ
            v = normal.y / sumXYZ
            w = normal.z / sumXYZ

            if w < 0:
                newU = (1 - abs(v)) * (1 if u >= 0 else -1)
                newV = (1 - abs(u)) * (1 if v >= 0 else -1)
                u,v = newU, newV

            result = Vector(((u+1)/2 , (v+1)/2))
            self.packNormalDic[index] = Vector(result)
            
    def ComputSmoothNormalMesh(self, mesh):
        mesh.calc_tangents(uvmap='MainUV')
        mesh.update()
                
        for loop in mesh.loops:
            vertIndex = loop.vertex_index
            tangent = loop.tangent.normalized()
            normal = loop.normal.normalized()
            bitangent = loop.bitangent.normalized()
            tbn = Matrix((tangent, bitangent, normal)).transposed()

            vertNormal = Vector(mesh.vertices[vertIndex].normal)
            smoothNormal = vertNormal @ tbn
            smoothNormal.normalize()

            # # Convert Blender's coordinate system (right-handed) to Unity's (left-handed)
            self.smoothNormalDic[loop.index] = Vector(smoothNormal)
        #八面体打包 
        self.octahedron_pack()

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
            # uvLayer.uv[loop.index].vector = (self.smoothNormalDic[loop.index].x, self.smoothNormalDic[loop.index].y)
            uvLayer.uv[loop.index].vector = self.packNormalDic[loop.index]
            
        # if "OutlineUV1" not in mesh.uv_layers.keys():
        #     uvLayer = mesh.uv_layers.new(name = "OutlineUV1")
        # else:
        #     self.report({'WARNING'},"OutlineUV already exists, and we rewrite it.")
        #     uvLayer = mesh.uv_layers["OutlineUV1"]
        # for loop in mesh.loops:
        #     uvLayer.uv[loop.index].vector = Vector((self.smoothNormalDic[loop.index].z, 0))
    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None

    def execute(self, context: bpy.types.Context):
        self.packNormalDic   = {}
        self.smoothNormalDic = {}

        objects = context.selected_objects
        for object in objects:
            mesh = object.data
            self.OutlineNormalExecute(mesh)
        
        self.clean_containers()
        return {'FINISHED'}