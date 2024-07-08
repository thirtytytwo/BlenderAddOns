import bpy

from addons.AddonOperators import ComputeOutlineNormalOperator

class ComputeOutlineNormalPannel(bpy.types.Panel):
    bl_label = "Compute Outline Normal"
    bl_idname = "SCENE_PT_ComputeOutlineNormal"
    bl_category = "Outline Normal Plugin"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    
    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.operator(ComputeOutlineNormalOperator.bl_idname, text="start compute")
    
    @classmethod    
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None