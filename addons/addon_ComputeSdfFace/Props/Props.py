import bpy

TextureSize = [
    (128, "128", "128"),
    (256, "256", "256"),
    (512, "512", "512"),
    (1024, "1024", "1024"),
    (2048, "2048", "2048")
]

class GeneratedImage(bpy.types.PropertyGroup):
    image: bpy.props.PointerProperty(type=bpy.types.Image)
    name: bpy.props.StringProperty(name="Image Name")

class SDFGenteratorProp(bpy.types.PropertyGroup):
    Resolution : bpy.props.EnumProperty(
        name="Resolution", 
        items = TextureSize, 
        default = 128)
    
    Iteration : bpy.props.IntProperty(
        name = "Iteration",
        default = 1,
        min = 1,
        max = 10
        )
    
    generated_images: bpy.props.CollectionProperty(type=GeneratedImage)