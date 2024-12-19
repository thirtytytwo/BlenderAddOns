
import bpy
from enum import Enum

Resolustion = [
    ("128", "128", "128", 128),
    ("256", "256", "256", 256),
    ("512", "512", "512", 512),
    ("1024", "1024", "1024", 1024),
    ("2048", "2048", "2048", 2048)
]

class SDFTextures(bpy.types.PropertyGroup):
    image: bpy.props.PointerProperty(type=bpy.types.Image)# type: ignore

class SdfProperties(bpy.types.PropertyGroup):
    Iterations: bpy.props.IntProperty(
        name="Iterations ",
        default=5,
        min=1,
        max=10,
        description="iterations when generate sdf base tex"
    ) # type: ignore
    Resolution: bpy.props.EnumProperty(
        name="Resolution",
        items=Resolustion,
        default="512",
        description="Resolution of the generated texture"
    ) # type: ignore
    GeneratedTextures: bpy.props.CollectionProperty(type=SDFTextures)# type: ignore
