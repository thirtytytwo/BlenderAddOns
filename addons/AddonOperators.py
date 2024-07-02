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
        result0 = tangent.normalized()
        result1 = normal - normal.dot(result0) * result0
        result1 = result1.normalized()
        return result0, result1
    
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
            
            #顶点, UV
            v0 = face.loops[0].vert.co
            v1 = face.loops[1].vert.co
            v2 = face.loops[2].vert.co
            
            uv0 = face.loops[0][uv_layer].uv
            uv1 = face.loops[1][uv_layer].uv
            uv2 = face.loops[2][uv_layer].uv
            
            ####计算TBN矩阵####
            #选取切线基(最短两条三角边)
            len0 = (v0 - v1).length
            len1 = (v0 - v2).length
            len2 = (v1 - v2).length
            if len0 >= len1 and len0 >= len2:
                edge0 = v0 - v2
                edge1 = v1 - v2
                delta_uv0 = uv0 - uv2
                delta_uv1 = uv1 - uv2
            elif len1 >= len0 and len1 >= len2: 
                edge0 = v0 - v1
                edge1 = v2 - v1
                delta_uv0 = uv0 - uv1
                delta_uv1 = uv2 - uv1
            else:
                edge0 = v2 - v0
                edge1 = v1 - v0
                delta_uv0 = uv2 - uv0
                delta_uv1 = uv1 - uv0
            #计算切线
            f = 1.0 / (delta_uv0.x * delta_uv1.y - delta_uv0.y * delta_uv1.x)
            tangent = Vector((f * (delta_uv1.y * edge0.x - delta_uv0.y * edge1.x),
                              f * (delta_uv1.y * edge0.y - delta_uv0.y * edge1.y),
                              f * (delta_uv1.y * edge0.z - delta_uv0.y * edge1.z)
                            )).normalized()
            #计算法线
            normal = edge1.cross(edge0).normalized()
            #切线法线正交化
            tangent_norm, normal_norm = self.ortho_normalize(tangent, normal)
            #副切线
            bitangent = tangent_norm.cross(normal_norm).normalized()
            #TBN矩阵
            tbn_matrix = Matrix((tangent_norm, bitangent, normal_norm)).transposed()
            
            #写入数据到字典(重复的法线需要剔除)
            for loop in face.loops:
                index_vector = Vector(loop.vert.co).freeze()
                index = loop.index
                
                if index_vector in self.same_normal_dic:
                    flag = False
                    for same_normal in self.same_normal_dic[index_vector]:
                        if same_normal == normal_norm:
                            flag = True
                            break
                    if flag:
                        continue
                    else:
                        self.same_normal_dic[index_vector].append(same_normal)
                else:
                    self.same_normal_dic[index_vector] = [normal_norm]
                
                self.tbn_matrix_dic[index] = tbn_matrix
                if index_vector not in self.sum_normal_dic:
                    self.sum_normal_dic[index_vector] = normal_norm
                else:
                    self.sum_normal_dic[index_vector] += normal_norm
        
        #得到平滑法线后转入TBN空间
        for face in bm.faces:
            for loop in face.loops:
                index = loop.index
                index_vector = Vector(loop.vert.co).freeze()
                
                sum_normal = self.sum_normal_dic[index_vector]
                print(sum_normal)
                sum_normal = sum_normal.normalized()
                
                tbn_matrix = self.tbn_matrix_dic[index]
                
                smooth_normal = tbn_matrix @ sum_normal
                smooth_normal.normalize()
                
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