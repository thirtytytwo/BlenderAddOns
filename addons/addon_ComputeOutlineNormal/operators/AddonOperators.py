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
        
        vertNormalDict = {} #存储顶点法线的字典 key：顶点索引 value：顶点法线
        vertDataCombos = {} #用于检查顶点重复数据的set，key：顶点索引 value：顶点数据
        vertNum = 0
        for loop in mesh.loops:
            vertIndex = loop.vertex_index
            normal = loop.normal
            combo = [round(normal.x, 4), round(normal.y, 4), round(normal.z, 4)]
            for uvLayer in mesh.uv_layers:
                if uvLayer.name == "OutlineUV":
                    continue
                uv = uvLayer.data[loop.index].uv
                # combo.extend([uv.x, uv.y])  
            
            comboTuple = tuple(combo)
            if vertIndex not in vertDataCombos:
                vertDataCombos[vertIndex] = set()
            if comboTuple not in vertDataCombos[vertIndex]:
                vertDataCombos[vertIndex].add(comboTuple)
                vertNum += 1
                if vertIndex not in vertNormalDict:
                    vertNormalDict[vertIndex] = Vector(normal)
                else:
                    vertNormalDict[vertIndex] += Vector(normal)
        print("vertNum: ", vertNum)
        for loop in mesh.loops:
            tangent = loop.tangent
            normal = loop.normal
            bitangent = loop.bitangent
            tbn = Matrix((tangent, bitangent, normal)).transposed()
        
            vertIndex= loop.vertex_index
            vertNormal = vertNormalDict[vertIndex].normalized()
            smoothNormal = vertNormal @ tbn
            smoothNormal.normalize()

            self.smoothNormalDic[loop.index] = smoothNormal
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
            uvLayer.uv[loop.index].vector = Vector(self.packNormalDic[loop.index])

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