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
            result = Vector(((result.x * 0.5 + 0.5), (result.y * 0.5 + 0.5)))
            self.pack_normal_dic[index] = Vector(result)
            
    def compute_smooth_normals(self, mesh):
        mesh.free_tangents()
        mesh.calc_tangents(uvmap='UVSet0')
        for loop in mesh.loops:
            index_vector = Vector(mesh.vertices[loop.vertex_index].co).freeze()
            normal = loop.normal
            
            if index_vector not in self.sum_normal_dic:
                self.sum_normal_dic[index_vector] = Vector(normal)
            else:
                self.sum_normal_dic[index_vector] += Vector(normal)
        #得到平滑法线后转入TBN空间
        for loop in mesh.loops:
            index_vector = Vector(mesh.vertices[loop.vertex_index].co).freeze()
            tangent = loop.tangent
            normal = loop.normal
            bitangent = loop.bitangent
            tbn_matrix = Matrix((tangent, bitangent, normal)).transposed()
        
            sum_normal = self.sum_normal_dic[index_vector]
            sum_normal.normalize()
        
            smooth_normal = sum_normal @ tbn_matrix
            smooth_normal.normalize()
            
            smooth_normal = Vector((-sum_normal.x, sum_normal.y, sum_normal.z))
            self.smooth_normal_dic[loop.index] = smooth_normal
        self.octahedron_pack()

    def add_custom_data_layer(self, mesh):
        #计算
        self.compute_smooth_normals(mesh)
        #写入数据
        if "OutlineUV" not in mesh.uv_layers.keys():
            uv_layer = mesh.uv_layers.new(name = "OutlineUV")
        else:
            self.report({'WARNING'}, "OutlineUV already exists, and we rewrite it.")
            uv_layer = mesh.uv_layers["OutlineUV"]
        
        for loop in mesh.loops:
            # TODO:不能单纯loop写入,因为unity会根据顶点对应UV不同分出多的顶点
            uv_layer.uv[loop.index].vector = Vector(self.pack_normal_dic[loop.index])

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