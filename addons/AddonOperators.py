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
    tangent_dic       :Dict[int, Vector]

    def clean_containers(self):
        self.sum_normal_dic.clear()
        self.pack_normal_dic.clear()
        self.smooth_normal_dic.clear()
        self.same_normal_dic.clear()
        self.tangent_dic.clear()
        
    def ortho_normalize(self, tangent, normal):
        result = Vector((tangent - (tangent.dot(normal) * normal))).normalized()
        return result
    
    def octahedron_pack(self):
        for index, IN in self.smooth_normal_dic.items():
            IN = Vector(IN).normalized()
            sum_xyz = (math.fabs(IN.x) + math.fabs(IN.y) + math.fabs(IN.z))
            
            u = IN.x / sum_xyz
            v = IN.y / sum_xyz
            w = IN.z / sum_xyz

            if w < 0.0:
                result = Vector(((1 - math.fabs(v)) * (1 if u >= 0 else -1), (1 - math.fabs(u)) * (1 if v >= 0 else -1)))
            else:
                result = Vector((u, v))
            result = Vector(((result.x * 0.5 + 0.5), (result.y * 0.5 + 0.5)))
            self.pack_normal_dic[index] = Vector(result)
            
    def compute_smooth_normals(self, bm):
        uv_layer = bm.loops.layers.uv[0]
        for face in bm.faces:
            normal = face.normal
            for loop in face.loops:
                index_vector = Vector(loop.vert.co).freeze()

                angle = loop.calc_angle()
                radians = math.radians(angle)
                val = radians / (2 * math.pi)
                
                if index_vector not in self.sum_normal_dic:
                    self.sum_normal_dic[index_vector] = Vector(normal) * val
                else:
                    self.sum_normal_dic[index_vector] += Vector(normal) * val
        #得到平滑法线后转入TBN空间
        for face in bm.faces:
            # v0 = face.loops[0].vert.co
            # v1 = face.loops[1].vert.co
            # v2 = face.loops[2].vert.co

            # uv0 = face.loops[0][uv_layer].uv
            # uv1 = face.loops[1][uv_layer].uv
            # uv2 = face.loops[2][uv_layer].uv

            # edge1 = v1 - v2
            # edge2 = v0 - v2

            # deltaUV1 = uv1 - uv2
            # deltaUV2 = uv0 - uv1

            # f = 1.0 / (deltaUV1.x * deltaUV2.y - deltaUV2.x * deltaUV1.y)
            # tangent = Vector((edge1 * deltaUV2.y - edge2 * deltaUV1.y) * f).normalized()
            # normal = face.normal
            # bitangent = normal.cross(tangent).normalized()
            # tbn_matrix = Matrix((tangent, bitangent, normal)).transposed()
            
            for loop in face.loops:
                index_vector = Vector(loop.vert.co).freeze()

                v0 = loop.vert.co
                v1 = loop.link_loop_prev.vert.co
                v2 = loop.link_loop_next.vert.co

                uv0 = loop[uv_layer].uv
                uv1 = loop.link_loop_prev[uv_layer].uv
                uv2 = loop.link_loop_next[uv_layer].uv

                edge1 = v1 - v0
                edge2 = v2 - v0

                deltaUV1 = uv1 - uv0
                deltaUV2 = uv2 - uv0

                f = 1.0 / (deltaUV1.x * deltaUV2.y - deltaUV2.x * deltaUV1.y)
                tangent = Vector((edge1 * deltaUV2.y - edge2 * deltaUV1.y) * f).normalized()
                normal = face.normal
                bitangent = normal.cross(tangent).normalized()
                tbn_matrix = Matrix((tangent, bitangent, normal)).transposed()
            
                sum_normal = self.sum_normal_dic[index_vector]
                sum_normal.normalize()
            
                smooth_normal = sum_normal @ tbn_matrix
                smooth_normal.normalize()
                
                self.tangent_dic[loop.index] = tangent
                self.smooth_normal_dic[loop.index] = smooth_normal
        self.octahedron_pack()

    def add_custom_data_layer(self, mesh):
        #转换bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)
        #计算
        self.compute_smooth_normals(bm)
        
        #写入数据
        if "Tangent" not in bm.loops.layers.float_vector:
            bm.loops.layers.float_vector.new("Tangent")
        if "OutlineUV" not in bm.loops.layers.uv:
            bm.loops.layers.uv.new("OutlineUV")
        else:
            self.report({'WARNING'}, "OutlineUV already exists, and we rewrite it.")
        uv_layer = bm.loops.layers.uv["OutlineUV"]
        tangent_layer = bm.loops.layers.float_vector["Tangent"]
        
        for face in bm.faces:
            for loop in face.loops:
                # TODO:不能单纯loop写入,因为unity会根据顶点对应UV不同分出多的顶点
                loop[uv_layer].uv = self.pack_normal_dic[loop.index]
                loop[tangent_layer] = self.tangent_dic[loop.index]
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
        self.same_normal_dic   = {}
        self.tangent_dic       = {}
        
        objects = context.selected_objects
        for object in objects:
            mesh = object.data
            self.add_custom_data_layer(mesh)
        
        self.clean_containers()
        return {'FINISHED'}