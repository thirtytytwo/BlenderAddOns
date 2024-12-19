import bpy

class ComputeSdfFacePanel(bpy.types.Panel):
    bl_label = "Compute Sdf Face"
    bl_idname = "SCENE_PT_ComputeSdfFace"
    bl_category = "Sdf Face Plugin"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    
    def draw(self, context: bpy.types.Context):
        layout = self.layout
        row = layout.row()
        row.label(text = "SDF Generator")
        
        prop = context.scene.SdfProperties
        row = layout.row()
        row.prop(prop, "Iterations")
        row.prop(prop, "Resolution")
        
        col = layout.column()
        col.operator("object.sdf_texturegenerate", text = "Generate")
        
        # Display generated images
        if len(prop.GeneratedTextures) > 0:
            col.label(text = "Generated Images")
            col.prop(prop, "GeneratedTextures")

    @classmethod    
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None