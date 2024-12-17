import bpy
from bpy.props import StringProperty
from bpy_extras.image_utils import load_image

class SdfTextureGenerateOperator(bpy.types.Operator):
    bl_idname = "object.sdf_texturegenerate"
    bl_label = "SdfTextureGenerator"

    sdf_texture_size = bpy.props.IntProperty(name="Texture Size", default=512)
    export_path = StringProperty(name="Export Path", subtype='FILE_PATH')

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        obj = context.active_object
        if not obj or not obj.data.uv_layers.active:
            self.report({'ERROR'}, "No active object with UV map found")
            return {'CANCELLED'}
        
        uv_layer = obj.data.uv_layers.active.data
        image = bpy.data.images.new("UV_Texture", width=self.sdf_texture_size, height=self.sdf_texture_size)
        
        # Generate image based on UVs
        for poly in obj.data.polygons:
            for loop_idx in range(poly.loop_start, poly.loop_start + poly.loop_total):
                uv = uv_layer[loop_idx].uv
                x = int(uv.x * self.sdf_texture_size)
                y = int((1 - uv.y) * self.sdf_texture_size)
                # Simple example: set pixel to white
                image.pixels[(y * self.sdf_texture_size + x) * 4] = 1.0  # R
                image.pixels[(y * self.sdf_texture_size + x) * 4 + 1] = 1.0  # G
                image.pixels[(y * self.sdf_texture_size + x) * 4 + 2] = 1.0  # B
                image.pixels[(y * self.sdf_texture_size + x) * 4 + 3] = 1.0  # A

        image.filepath_raw = self.export_path
        image.file_format = 'PNG'
        image.save()
        
        return {"FINISHED"}

