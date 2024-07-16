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

    same_normal_dic   :Dict[Vector, list[Vector]]

    def clean_containers(self):
        self.sum_normal_dic.clear()
        self.pack_normal_dic.clear()
        self.smooth_normal_dic.clear()
        self.same_normal_dic.clear()
        
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
            val = Vector(result)
            result = Vector(((val.x * 0.5 + 0.5), (val.y * 0.5 + 0.5)))
            self.pack_normal_dic[index] = Vector(result)
            
    def compute_smooth_normals(self, bm):
        uv_layer = bm.loops.layers.uv[0]
        for face in bm.faces:
            normal = Vector(face.normal).normalized().freeze()
            for loop in face.loops:
                index_vector = Vector(loop.vert.co).freeze()
                
                if index_vector not in self.sum_normal_dic:
                    self.sum_normal_dic[index_vector] = normal
                else:
                    self.sum_normal_dic[index_vector] = self.sum_normal_dic[index_vector] + normal
        
        #得到平滑法线后转入TBN空间
        for face in bm.faces:
            #逆序
            rever_loops = list(reversed(face.loops))
            
            #根据逆序算面切线
            v0 = rever_loops[0].vert.co
            v1 = rever_loops[1].vert.co
            v2 = rever_loops[2].vert.co

            #unity 顶点逆序，但是uv不受影响
            uv0 = rever_loops[0][uv_layer].uv
            uv1 = rever_loops[1][uv_layer].uv
            uv2 = rever_loops[2][uv_layer].uv
            
            dist_v0_v1 = (v1 - v0).length
            dist_v0_v2 = (v2 - v0).length
            dist_v1_v2 = (v2 - v1).length
            
            if dist_v0_v1 > dist_v0_v2 and dist_v0_v1 > dist_v1_v2:
                # v0_v1 是最长边，所以v2是两条短边的交点
                v0, v1, v2 = v2, v0, v1
                uv0, uv1, uv2 = uv2, uv0, uv1
            elif dist_v0_v2 > dist_v0_v1 and dist_v0_v2 > dist_v1_v2:
                # v0_v2 是最长边，所以v1是两条短边的交点
                v0, v1, v2 = v1, v2, v0
                uv0, uv1, uv2 = uv1, uv2, uv0

            #计算切线
            deltaPos1 = v1 - v0
            deltaPos2 = v2 - v0

            deltaUV1 = uv1 - uv0
            deltaUV2 = uv2 - uv0

            r = 1.0 / (deltaUV1.x * deltaUV2.y - deltaUV1.y * deltaUV2.x)
            tangent = Vector((deltaPos1 * deltaUV2.y - deltaPos2 * deltaUV1.y) * r)

            normal = Vector(face.normal)
            tangent = self.ortho_normalize(tangent, normal)
            bitangent = tangent.cross(normal).normalized()
            
            tbn_matrix = Matrix((tangent, bitangent, normal)).transposed()
            for loop in face.loops:
                index_vector = Vector(loop.vert.co).freeze()
                
                sum_normal = self.sum_normal_dic[index_vector]
                sum_normal.normalize()
                
                smooth_normal = sum_normal @ tbn_matrix
                smooth_normal.normalize()
                
                self.smooth_normal_dic[loop.index] = smooth_normal
        self.octahedron_pack()

    def add_custom_data_layer(self, mesh):
        #转换bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)
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
        self.same_normal_dic   = {}
        
        objects = context.selected_objects
        for object in objects:
            mesh = object.data
            self.add_custom_data_layer(mesh)
        
        self.clean_containers()
        return {'FINISHED'}