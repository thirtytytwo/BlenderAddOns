import bpy

class SDFPanel(bpy.types.Panel):
    bl_label = "SDF Generator"
    bl_idname = "OBJECT_PT_sdf_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SDF Generator'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "object_type")
        layout.prop(scene, "uvmap_type")
