import bmesh
import bpy
import math
import numpy
from mathutils import Vector


from addons.test_addon.config import __addon_name__
from addons.test_addon.preference.AddonPreferences import ExampleAddonPreferences


# This Example Operator will scale up the selected object
class ComputeOutlineNormalOperator(bpy.types.Operator):
    '''ExampleAddon'''
    bl_idname = "object.compute_outline_normal"
    bl_label = "ComputeOutlineNormalOperator"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    def octahedron_pack(self, array):
        pack_array = numpy.zeros((len(array), 2))
        for index in range(len(array)):
            IN = array[index]
            IN /= (math.fabs(IN[0]) + math.fabs(IN[1]) + math.fabs(IN[2]))
            if IN[2] < 0.0:
                result = Vector((1.0 - math.fabs(IN[1]) * (IN[0] >= 0 if 1.0 else -1.0), 1.0 - math.fabs(IN[0]) * (IN[1] >= 0 if 1.0 else -1.0)))
            else:
                result = Vector((IN[0], IN[1]))
            result = Vector(((result.x * 0.5 + 0.5), (result.y * 0.5 + 0.5)))
            pack_array[index] = result
            return pack_array

    def compute_smooth_normals(self, mesh):
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        smooth_normal_array = numpy.zeros((len(bm.verts), 3))
        for face in bm.faces:
            normal = face.normal
            verts = face.verts[:]
            for i in range(3):
                d0 = verts[(i + 1) % 3].co - verts[i].co
                d1 = verts[(i + 2) % 3].co - verts[i].co
                angle = d0.angle(d1)
                cos_angle = math.cos(angle)
                index = verts[i].index
                smooth_normal_array[index] += normal * cos_angle
        bm.free()
        return self.octahedron_pack(smooth_normal_array)

    def add_custom_data_layer(self, mesh):
        if "custom_data" not in mesh.attributes:
            mesh.attributes.new(name='custom_data', type='FLOAT2', domain='POINT')

        attr = mesh.attributes["custom_data"].data
        for i in range(len(attr)):
            array = self.compute_smooth_normals(mesh)
            attr[i].vector = Vector((array[i][0], array[i][1]))

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None

    def execute(self, context: bpy.types.Context):
        objects = context.selected_objects
        for object in objects:
            mesh = object.data
            self.add_custom_data_layer(mesh)
        return {'FINISHED'}
