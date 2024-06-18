import bmesh
import bpy
import math
from typing import Dict
from mathutils import Vector

# This Example Operator will scale up the selected object
class ComputeOutlineNormalOperator(bpy.types.Operator):
    '''ExampleAddon'''
    bl_idname = "object.compute_outline_normal"
    bl_label = "ComputeOutlineNormalOperator"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    pack_normal_dic :Dict[int, Vector]
    smooth_normal_dic :Dict[int, Vector]
    
    def __init__(self):
        # 在构造函数中初始化字典
        self.pack_normal_dic = {}
        self.smooth_normal_dic = {}
    
    def octahedron_pack(self):
        for index, IN in self.smooth_normal_dic.items():
            IN = Vector(IN)  # Ensure IN is a Vector if not already
            IN /= (math.fabs(IN.x) + math.fabs(IN.y) + math.fabs(IN.z))
            if IN.z < 0.0:
                result = Vector((1.0 - math.fabs(IN.y) * (1.0 if IN.x >= 0 else -1.0), 1.0 - math.fabs(IN.x) * (1.0 if IN.y >= 0 else -1.0)))
            else:
                result = Vector((IN.x, IN.y))
            result = Vector(((result.x * 0.5 + 0.5), (result.y * 0.5 + 0.5)))
            self.pack_normal_dic[index] = result
            
    def compute_smooth_normals(self, bm):
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        for face in bm.faces:
            normal = face.normal
            verts = face.verts[:]
            for i in range(3):
                d0 = verts[(i + 1) % 3].co - verts[i].co
                d1 = verts[(i + 2) % 3].co - verts[i].co
                angle = d0.dot(d1)
                cosine = abs(angle / (d0.length * d1.length))
                index = verts[i].index
                
                if index not in self.smooth_normal_dic.keys():
                    self.smooth_normal_dic[index] = normal.xyz * cosine
                else:
                    self.smooth_normal_dic[index] += normal.xyz * cosine
        self.octahedron_pack()

    def add_custom_data_layer(self, mesh):
        bm = bmesh.new()
        bm.from_mesh(mesh)
        
        self.compute_smooth_normals(bm)
        
        uv_layer = bm.loops.layers.uv.new("UVSet3")
        
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        for face in bm.faces:
            for loop in face.loops:
                #TODO: 我计算的数据是基于顶点的，但是UV基于面拐，我需要只把他放在顶点第一次出现的时候，其他时候就置0
                if loop.vert.index not in self.pack_normal_dic.keys():
                    loop[uv_layer].uv = (0.0, 0.0)
                else:
                    loop[uv_layer].uv = self.pack_normal_dic[loop.vert.index]
        
        bm.to_mesh(mesh)
        bm.free()
        
        mesh.update()

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None

    def execute(self, context: bpy.types.Context):
        objects = context.selected_objects
        for object in objects:
            mesh = object.data
            self.add_custom_data_layer(mesh)
        return {'FINISHED'}