import bpy


class ComputeOutlineNormalPanel(bpy.types.Panel):
    bl_label = "Compute Outline Normal"
    bl_idname = "SCENE_PT_ComputeOutlineNormal"
    bl_category = "Outline Normal Plugin"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    
    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.operator("object.compute_outline_normal", text="Compute")
        layout.operator("object.modifymeshvertex", text="Modify")
    
    @classmethod    
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None
