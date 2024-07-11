import bmesh
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
            sum_xyz = (math.fabs(IN.x) + math.fabs(IN.y) + math.fabs(IN.z))
            if sum_xyz == 0.0:
                result = Vector((0.5, 0.5))
                self.pack_normal_dic[index] = result
                continue
            
            u = IN.x / sum_xyz
            v = IN.y / sum_xyz
            w = IN.z / sum_xyz

            if w < 0.0:
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
            # for i in range(3):
            #     index = face.loops[i].index
            #     index_vec = Vector(face.verts[i].co).freeze()
                
            #     v0 = face.loops[i].vert.co
            #     v1 = face.loops[(i+1)%3].vert.co
            #     v2 = face.loops[(i+2)%3].vert.co
            #     uv0 = face.loops[i][uv_layer].uv
            #     uv1 = face.loops[(i+1)%3][uv_layer].uv
            #     uv2 = face.loops[(i+2)%3][uv_layer].uv
            #     edge1 = v1 - v0
            #     edge2 = v2 - v0
            #     delta_uv1 = uv1 - uv0
            #     delta_uv2 = uv2 - uv0
                
            #     f = 1.0 / (delta_uv1.y * delta_uv2.x - delta_uv2.y * delta_uv1.x)
            #     tangent = Vector(f * (delta_uv1.y * edge2 - delta_uv2.y * edge1))
            #     normal = face.normal
            for loop in face.loops:
                index_vector = Vector(loop.vert.co).freeze()
                index = loop.index
                
                v0 = loop.vert.co
                v1 = loop.link_loop_next.vert.co
                v2 = loop.link_loop_prev.vert.co
                uv0 = loop[uv_layer].uv
                uv1 = loop.link_loop_next[uv_layer].uv
                uv2 = loop.link_loop_prev[uv_layer].uv
                edge0 = v2 - v0
                edge1 = v1 - v0
                delta_uv0 = uv2 - uv0
                delta_uv1 = uv1 - uv0
                f = 1.0 / (delta_uv0.x * delta_uv1.y - delta_uv0.y * delta_uv1.x)
                tangent=Vector((f * (delta_uv1.y * edge0.x - delta_uv0.y * edge1.x),
                                f * (delta_uv1.y * edge0.y - delta_uv0.y * edge1.y),
                                f * (delta_uv1.y * edge0.z - delta_uv0.y * edge1.z)
                                )).normalized()
                normal = face.normal
                tangent_norm = self.ortho_normalize(tangent, normal)
                bitangent = normal.cross(tangent_norm).normalized()
                print(tangent, tangent_norm)
                
                self.tbn_matrix_dic[index] = Matrix((tangent_norm, bitangent, normal)).transposed()
                
                if index_vector in self.same_normal_dic:
                    flag = False
                    for same_normal in self.same_normal_dic[index_vector]:
                        if same_normal == Vector(normal):
                            flag = True
                            break
                    if flag:
                        continue
                    else:
                        self.same_normal_dic[index_vector].append(Vector(normal))
                else:
                    self.same_normal_dic[index_vector] = [Vector(normal)]
                
                if index_vector not in self.sum_normal_dic:
                    self.sum_normal_dic[index_vector] = Vector(normal)
                else:
                    self.sum_normal_dic[index_vector] += Vector(normal)
        
        #得到平滑法线后转入TBN空间
        for face in bm.faces:
            for loop in face.loops:
                index = loop.index
                index_vector = Vector(loop.vert.co).freeze()
                
                sum_normal = self.sum_normal_dic[index_vector]
                sum_normal = sum_normal.normalized()
                
                tbn_matrix = self.tbn_matrix_dic[index] 
                
                smooth_normal = tbn_matrix @ sum_normal
                self.smooth_normal_dic[index] = smooth_normal
        
        self.octahedron_pack()

    def add_custom_data_layer(self, mesh):
        #转换bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()  

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
        
        #计算
        self.compute_smooth_normals(bm)
        
        #写入数据
        if "OutlineUV" not in bm.loops.layers.uv:
            bm.loops.layers.uv.new("OutlineUV")
        else:
            self.report({'WARNING'}, "OutlineUV already exists, and we rewrite it.")
        uv_layer = bm.loops.layers.uv["OutlineUV"]
        
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
        self.sum_normal_dic    = {}
        self.pack_normal_dic   = {}
        self.smooth_normal_dic = {}
        self.tbn_matrix_dic    = {}
        self.same_normal_dic   = {}
        
        objects = context.selected_objects
        for object in objects:
            mesh = object.data
            self.add_custom_data_layer(mesh)
        
        self.clean_containers()
        return {'FINISHED'}