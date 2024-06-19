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
        
        self.tangent_dic        = {}
        self.bitangent_dic      = {}
        self.normal_dic         = {}
        
    def clean_container(self):
        self.pack_normal_dic.clear()
        self.smooth_normal_dic.clear()
        self.sum_normal_dic.clear()
        
        self.tangent_dic.clear()
        self.bitangent_dic.clear()
        self.normal_dic.clear()
    
    def octahedron_pack(self):
        for index, IN in self.smooth_normal_dic.items():
            IN = Vector(IN)
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
            verts = face.verts[:]
            for i in range(len(verts) - 1):
                #compute vert
                #TODO:是不是坐标轴不一样需要在这里做处理 
                v0 = verts[i].co
                v1 = verts[(i + 1) % 3].co
                v2 = verts[(i + 2) % 3].co
                
                #compute dir
                dir0 = v1 - v0
                dir1 = v2 - v0
                dot_val = float(dir0.dot(dir1))
                cosine = math.fabs(math.cos(dot_val))
                
                index = verts[i].index
                
                #compute T B N 
                normal = dir0.cross(dir1).normalized()
            
                tangent = dir0
                bitangent = dir1
                
                tangent = tangent.cross(normal)
                bitangent = bitangent.cross(normal)
                tangent.normalize()
                bitangent.normalize()
                
                #write into dic
                self.tangent_dic[index] = tangent
                self.bitangent_dic[index] = bitangent
                self.normal_dic[index] = normal
            
                if index not in self.smooth_normal_dic.keys():
                    self.sum_normal_dic[index] = normal.xyz * cosine
                else:
                    self.sum_normal_dic[index] += normal.xyz * cosine
        
        #求和后的平滑法线转切线空间
        for index, IN in self.sum_normal_dic.items():
            IN.normalize()
            
            tbn_matrix = Matrix((self.tangent_dic[index], self.bitangent_dic[index], self.normal_dic[index]))
            tbn_matrix.transpose()
            normal = tbn_matrix @ IN
            normal.normalize()
            
            self.smooth_normal_dic[index] = normal
        
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