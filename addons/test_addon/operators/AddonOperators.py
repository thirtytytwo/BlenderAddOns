import bmesh
import bpy
import math
from typing import Dict
from mathutils import Vector, Matrix

# This Example Operator will scale up the selected object
class ComputeOutlineNormalOperator(bpy.types.Operator):
    '''ExampleAddon'''
    bl_idname = "object.compute_outline_normal"
    bl_label = "ComputeOutlineNormalOperator"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    pack_normal_dic   :Dict[int, Vector]
    sum_normal_dic    :Dict[int, Vector]
    smooth_normal_dic :Dict[int, Vector]
    
    tangent_dic       :Dict[int, Vector]
    bitangent_dic     :Dict[int, Vector]
    normal_dic        :Dict[int, Vector]
    
    def __init__(self):
        # 在构造函数中初始化字典
        self.pack_normal_dic    = {}
        self.smooth_normal_dic  = {}
        self.sum_normal_dic     = {}
        
    def clean_container(self):
        self.pack_normal_dic.clear()
        self.smooth_normal_dic.clear()
        self.sum_normal_dic.clear()

    def octahedron_pack(self):
        for index, IN in self.smooth_normal_dic.items():
            IN = Vector(IN).normalized()
            
            sum_xyz = math.fabs(IN.x) + math.fabs(IN.y) + math.fabs(IN.z)
            
            u = IN.x / sum_xyz
            v = IN.y / sum_xyz
            
            if IN.z < 0.0:
                u = (1 - math.fabs(v) * (1 if u >= 0 else -1))
                v = (1 - math.fabs(u) * (1 if v >= 0 else -1))
            result = Vector(((u * 0.5 + 0.5), (v * 0.5 + 0.5)))
            self.pack_normal_dic[index] = result
            
    def compute_smooth_normals(self, bm):
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        for face in bm.faces:
            loops = face.loops
            for loop in loops:
                #compute vert
                v0 = loop.vert.co
                v1 = loop.link_loop_next.vert.co
                v2 = loop.link_loop_prev.vert.co
                
                #变换手系
                transform_matrix = Matrix([
                    [1, 0, 0],
                    [0, 0, 1],
                    [0, -1, 0]
                ])
                
                v0 = transform_matrix @ v0
                v1 = transform_matrix @ v1
                v2 = transform_matrix @ v2

                dir0 = (v1 - v0).normalized()
                dir1 = (v2 - v0).normalized()
                
                normal = dir0.cross(dir1).normalized()
                
                cos_theta = dir0.dot(dir1) / (dir0.length * dir1.length)
                theta = math.acos(cos_theta)
                weight = (theta / math.pi)
                
                index = loop.vert.index
                
                if index not in self.sum_normal_dic.keys():
                    self.sum_normal_dic[index] = normal
                else:
                    self.sum_normal_dic[index] += normal * weight
                
        
        #求和后的平滑法线转切线空间
        for index, IN in self.sum_normal_dic.items():
            IN.normalize()
            self.smooth_normal_dic[index] = IN
            
        self.octahedron_pack()

    def add_custom_data_layer(self, mesh):
        bm = bmesh.new()
        bm.from_mesh(mesh)
        
        self.compute_smooth_normals(bm)
        
        uv_layer = bm.loops.layers.uv.new("UVSet3")
        
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        for face in bm.faces:
            for loop in face.loops:
                saved_index = []
                if loop.vert.index not in saved_index:
                    if loop.vert.index in self.pack_normal_dic.keys():
                        loop[uv_layer].uv = self.pack_normal_dic[loop.vert.index]
                    saved_index.append(loop.vert.index)
                else:
                    loop[uv_layer].uv = (0.0, 0.0)
        
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
        
        self.clean_container()
        return {'FINISHED'}