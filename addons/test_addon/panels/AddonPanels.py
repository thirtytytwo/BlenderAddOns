import bpy

from addons.test_addon.config import __addon_name__
from addons.test_addon.operators.AddonOperators import ComputeOutlineNormalOperator
from common.i18n.i18n import i18n


class ExampleAddonPanel(bpy.types.Panel):
    bl_label = "Example Addon Side Bar Panel"
    bl_idname = "SCENE_PT_sample"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    # name of the side panel
    bl_category = "ExampleAddon"

    def draw(self, context: bpy.types.Context):
        addon_prefs = context.preferences.addons[__addon_name__].preferences
        layout = self.layout

        layout.operator(ComputeOutlineNormalOperator.bl_idname)

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None
