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
        
        # Use the existing material 'material002'
        mat = obj.data.materials.get('Material.002')    
        if not mat:
            self.report({'ERROR'}, "Material 'material002' not found on the object")
            return {'CANCELLED'}
        
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        
        # Create a new image for baking
        image = bpy.data.images.new("Baked_Texture", width=512, height=512)
        
        # Set bake settings
        bpy.context.scene.render.engine = 'CYCLES'
        
        # Select the object and set it active
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # Bake the image
        texNode = nodes.new(type='ShaderNodeTexImage')
        texNode.image = image
        bpy.ops.object.bake(type='EMIT', pass_filter={'COLOR'})
        
        # Save the baked image
        image.filepath_raw = "C:\\Users\\xy\\Desktop\\material002_bake.png"
        image.file_format = 'PNG'
        image.save()
        print("Baked image saved to", image.filepath_raw)
        
        return {"FINISHED"}

