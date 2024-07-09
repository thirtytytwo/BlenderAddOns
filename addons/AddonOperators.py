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
        
        for face in bm.faces:
            tangent = face.calc_tangent_edge_diagonal()
            normal = face.normal
            tangent = self.ortho_normalize(tangent, normal).normalized()
            bitangent = normal.cross(tangent).normalized()

            tbn_matrix = Matrix([tangent, bitangent, normal]).transposed()

            for loop in face.loops:
                index = loop.index
                index_vec = Vector(loop.vert.co).freeze()

                self.tbn_matrix_dic[index] = tbn_matrix

                self.sum_normal_dic[index_vec] = loop.vert.normal

        #得到平滑法线后转入TBN空间
        for face in bm.faces:
            for loop in face.loops:
                index = loop.index
                index_vec = Vector(loop.vert.co).freeze()
                
                sum_normal = self.sum_normal_dic[index_vec]
                sum_normal = sum_normal.normalized()
                
                tbn_matrix = self.tbn_matrix_dic[index] 
                
                smooth_normal = sum_normal @ tbn_matrix
                smooth_normal.normalize()

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