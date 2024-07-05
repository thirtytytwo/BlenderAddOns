import bmesh
import bpy
import math
from typing import Dict, List
from mathutils import Vector, Matrix

# This Example Operator will scale up the selected object
class ComputeOutlineNormalOperator(bpy.types.Operator):
    '''ExampleAddon'''
    bl_idname = "object.compute_outline_normal"
    bl_label = "ComputeOutlineNormalOperator"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    sum_normal_dic    :Dict[Vector, Vector]
    pack_normal_dic   :Dict[int, Vector]
    smooth_normal_dic :Dict[int, Vector]
    
    tbn_matrix_dic    :Dict[int, Matrix]
    
    same_normal_dic   :Dict[Vector, list[Vector]]

    def clean_containers(self):
        self.sum_normal_dic.clear()
        self.pack_normal_dic.clear()
        self.smooth_normal_dic.clear()
        self.tbn_matrix_dic.clear()
        self.same_normal_dic.clear()
        
    def ortho_normalize(self, tangent, normal):
        result = Vector((tangent - (tangent.dot(normal) * normal))).normalized()
        return result
    
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
            
    def compute_smooth_normals(self, bm):
        #检查UV
        if not bm.loops.layers.uv[0]:
            self.report({'ERROR'}, "No active UV")
            return {'CANCELED'}
        uv_layer = bm.loops.layers.uv[0]
        
        for face in bm.faces:
            #检查三角面 只允许三角面计算
            if len(face.verts)!= 3:
                self.report({'ERROR'}, "Only Triangles")
                return {'CANCELED'}
            for i in range(3):
                index = face.loops[i].index
                index_vec = Vector(face.verts[i].co).freeze()
                
                v0 = face.loops[i].vert.co
                v1 = face.loops[(i+1)%3].vert.co
                v2 = face.loops[(i+2)%3].vert.co
                uv0 = face.loops[i][uv_layer].uv    
                uv1 = face.loops[(i+1)%3][uv_layer].uv
                uv2 = face.loops[(i+2)%3][uv_layer].uv
                edge1 = v1 - v0
                edge2 = v2 - v0
                delta_uv1 = uv1 - uv0
                delta_uv2 = uv2 - uv0
                
                f = 1.0 / (delta_uv1.x * delta_uv2.y - delta_uv2.x * delta_uv1.y)
                tangent = Vector(f * (delta_uv2.y * edge1 - delta_uv1.y * edge2))
                normal = face.normal
                tangent = self.ortho_normalize(tangent, normal)
                bitangent = Vector(normal.cross(tangent)).normalized()
                tbn_matrix = Matrix((tangent,bitangent,normal)).transposed()
                
                self.tbn_matrix_dic[index] = tbn_matrix
                
                if index_vec in self.same_normal_dic:
                    flag = False
                    for same_normal in self.same_normal_dic[index_vec]:
                        if same_normal == Vector(normal):
                            flag = True
                            break
                    if flag:
                        continue
                    else:
                        self.same_normal_dic[index_vec].append(Vector(normal))
                else:
                    self.same_normal_dic[index_vec] = [Vector(normal)]
                
                if index_vec not in self.sum_normal_dic:   
                    self.sum_normal_dic[index_vec] = Vector(normal)
                else:
                    self.sum_normal_dic[index_vec] += Vector(normal)
        
        #得到平滑法线后转入TBN空间
        for face in bm.faces:
            for loop in face.loops:
                index = loop.index
                index_vec = Vector(loop.vert.co).freeze()
                
                sum_normal = self.sum_normal_dic[index_vec]
                sum_normal = sum_normal.normalized()
                
                tbn_matrix = self.tbn_matrix_dic[index]
                
                smooth_normal = sum_normal @ tbn_matrix
                self.smooth_normal_dic[index] = smooth_normal
        
        self.octahedron_pack()

    def add_custom_data_layer(self, mesh):
        #转换bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)  
        
        #计算
        self.compute_smooth_normals(bm)
        
        #写入数据
        if "UVSet3" not in bm.loops.layers.uv:
            bm.loops.layers.uv.new("UVSet3")
        else:
            self.report({'WARNING'}, "UVSet3 already exists, and we rewrite it.")
        uv_layer = bm.loops.layers.uv["UVSet3"]
        
        for face in bm.faces:
            for loop in face.loops:
                loop[uv_layer].uv = self.pack_normal_dic[loop.index]
        #传回网格
        bm.to_mesh(mesh)
        bm.free()

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None

    def execute(self, context: bpy.types.Context):
        self.sum_normal_dic = {}
        self.pack_normal_dic = {}
        self.smooth_normal_dic = {}
        self.tbn_matrix_dic = {}
        self.same_normal_dic = {}
        
        objects = context.selected_objects
        for object in objects:
            mesh = object.data
            self.add_custom_data_layer(mesh)
        
        self.clean_containers()
        return {'FINISHED'}