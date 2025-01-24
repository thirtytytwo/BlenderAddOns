import bpy

class EditorPanel(bpy.types.Panel):
    bl_label = "Compute Sdf Face"
    bl_idname = "SCENE_PT_ComputeSdfFace"
    bl_category = "Sdf Face Plugin"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    
    def draw(self, context: bpy.types.Context):
        layout = self.layout
        if len(context.selected_objects) == 0 or context.selected_objects[0].type != 'MESH':
            layout.label(text="Please select a mesh object.", icon='ERROR')
            return
        
        row = layout.row()
        row.label(text = "SDF Generator")
        
        prop = context.scene.SdfProperties
        row = layout.row()
        row.prop(prop, "Iterations")
        row.prop(prop, "Resolution")
        col = layout.column()
        col.prop(prop, "FaceFront")
        col.prop(prop, "FaceRight")
        
        col = layout.column()
        col.operator("object.sdf_med_gen", text = "Compute Medium Texture")
        
        # Display generated images
        if len(prop.FaceClampTextures) > 0:
            box = layout.box()
            box.label(text="SDF Textures")
            grid = box.grid_flow(row_major=True, columns=2, align=True)
            
            for i, tex in enumerate(prop.FaceClampTextures):
                if tex.image:
                    col = grid.column()
                    col.template_ID_preview(tex, "image", hide_buttons=True)

        col = layout.column()
        col.operator("object.sdf_ret_gen", text = "Compute Ret Texture")

    @classmethod    
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None