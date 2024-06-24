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
    
    tbn_matrix_dic    :Dict[int, Matrix]
    
    def __init__(self):
        # 在构造函数中初始化字典
        self.pack_normal_dic    = {}
        self.smooth_normal_dic  = {}
        self.sum_normal_dic     = {}
        
        self.tbn_matrix_dic     = {}
        
    def clean_container(self):
        self.pack_normal_dic.clear()
        self.smooth_normal_dic.clear()
        self.sum_normal_dic.clear()
        self.tbn_matrix_dic.clear()

    def octahedron_pack(self):
        for index, IN in self.smooth_normal_dic.items():
            IN = Vector(IN).normalized()
            
            sum_xyz = math.fabs(IN.x) + math.fabs(IN.y) + math.fabs(IN.z)
            
            u = IN.x / sum_xyz
            v = IN.y / sum_xyz
            
            if IN.z < 0.0:
                u = ((1 - math.fabs(v)) * (1 if u >= 0 else -1))
                v = ((1 - math.fabs(u)) * (1 if v >= 0 else -1))
            result = Vector(((u * 0.5 + 0.5), (v * 0.5 + 0.5)))
            self.pack_normal_dic[index] = result
            
    def compute_smooth_normals(self, mesh):
        #TODO:存储TBN的index 和 vertices的nidex不一致，可能导致TBN的dic读不到数据的问题
        #get TBN matrix
        for loop in mesh.loops:
            index = loop.vertex_index
            tangent = loop.tangent
            normal = loop.normal
            bitangent = loop.bitangent
            self.tbn_matrix_dic[index] = Matrix((tangent, bitangent, normal)).transpose()
        
        for tris in mesh.loop_triangles:
            for i in range(3):
                v0 = mesh.vertices[tris.vertices[i]].co
                v1 = mesh.vertices[tris.vertices[(i + 1) % 3]].co
                v2 = mesh.vertices[tris.vertices[(i + 2) % 3]].co
                
                dir0 = (v1 - v0).normalized()
                dir1 = (v2 - v0).normalized()
                
                theta = math.acos(dir0.dot(dir1))
                weight = theta / math.pi
                
                index = mesh.vertices[tris.vertices[i]].index
                if index not in self.sum_normal_dic.keys():
                    self.sum_normal_dic[index] = normal * weight
                else: 
                    self.sum_normal_dic[index] += normal * weight
                    
        #transform sum normals to tangent space and writ into smooth normal dic
        for index, IN in self.sum_normal_dic.items():
            IN.normalize()
            transform_matrix = self.tbn_matrix_dic.get(index)
            if transform_matrix is not None:
                transform_normal = transform_matrix @ IN
                self.smooth_normal_dic[index] = transform_normal
            
        self.octahedron_pack()

    def add_custom_data_layer(self, mesh):
        if not mesh.uv_layers.active:
            self.report({'ERROR'}, "No active UV")
            return {'CANCELED'}
        mesh.calc_tangents()
        
        self.compute_smooth_normals(mesh)
        
        if "UVSet3" not in mesh.uv_layers:
            mesh.uv_layers.new(name="UVSet3")
        
        

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