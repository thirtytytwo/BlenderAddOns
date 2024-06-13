import bmesh
import bpy
from mathutils import Vector

from addons.Test_Addon.config import __addon_name__
from addons.Test_Addon.preference.AddonPreferences import ExampleAddonPreferences


# This Example Operator will scale up the selected object
class ExampleOperator(bpy.types.Operator):
    '''ExampleAddon'''
    bl_idname = "object.example_ops"
    bl_label = "ExampleOperator"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    def add_custom_data_layer(self, obj):
        if "custom_data" not in obj.data.attributes:
            obj.data.attributes.new(name='custom_data', type='FLOAT2',domain='POINT')
        
        attr = obj.data.attributes["custom_data"].data
        for i in range(len(attr)):
            attr[i].vector = (1.0, 2.0)
    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None

    def execute(self, context: bpy.types.Context):
        objects = context.selected_objects
        for object in objects:
            self.add_custom_data_layer(object)
        return {'FINISHED'}
