
import bpy
from enum import Enum

Resolustion = [
    ("128", "128", "128", 128),
    ("256", "256", "256", 256),
    ("512", "512", "512", 512),
    ("1024", "1024", "1024", 1024),
    ("2048", "2048", "2048", 2048)
]
Direction = [
    ("+X", "+X", "+X", 0),
    ("+Y", "+Y", "+Y", 1),
    ("+Z", "+Z", "+Z", 2),
    ("-X", "-X", "-X", 3),
    ("-Y", "-Y", "-Y", 4),
    ("-Z", "-Z", "-Z", 5)
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
    LightAngle: bpy.props.FloatProperty(name="LightAngle", default=0, min=0, max=180, description="Light angle") # type: ignore
    SmoothArea: bpy.props.FloatProperty(name="SmoothArea", default=0.01, min=0.001, max=0.5, description="Smooth area") # type: ignore
    PreviewActive: bpy.props.BoolProperty(name="PreviewActive", default=False, description="Preview active") # type: ignore
    Resolution: bpy.props.EnumProperty(
        name="Resolution",
        items=Resolustion,
        default="512",
        description="Resolution of the generated texture"
    ) # type: ignore
    FaceFront : bpy.props.EnumProperty(
        name="FaceFront",
        items=Direction,
        default="+Y",
        description="Front face direction"
    )# type: ignore
    FaceRight : bpy.props.EnumProperty(
        name="FaceRight",
        items=Direction,
        default="+X",
        description="Right face direction"
    )# type: ignore
    FaceClampTextures: bpy.props.CollectionProperty(type=SDFTextures)# type: ignore
    GeneratedTexture: bpy.props.PointerProperty(type=bpy.types.Image) # type: ignore
