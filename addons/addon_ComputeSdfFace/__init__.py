
import bpy
from .Operators.FaceClampGener import FaceClampTexGenOperator
from .Operators.FaceShadowGener import FaceShadowTexGenOperator
from .Operators.SDFMaterialUpdater import SDFMaterialUpdateOperator
from .Operators.Cleaner import CleanOperator
from .Panels.ComputeSdfFacePanel import EditorPanel
from .PluginProps import SDFTextures, SdfProperties

def register(): 
    bpy.utils.register_class(SDFTextures)
    bpy.utils.register_class(SdfProperties)
    bpy.utils.register_class(CleanOperator)
    bpy.utils.register_class(SDFMaterialUpdateOperator)
    bpy.types.Scene.SdfProperties = bpy.props.PointerProperty(type=SdfProperties)
    bpy.utils.register_class(FaceClampTexGenOperator)
    bpy.utils.register_class(FaceShadowTexGenOperator)
    bpy.utils.register_class(EditorPanel)


def unregister(): 
    bpy.utils.unregister_class(FaceClampTexGenOperator)
    bpy.utils.unregister_class(FaceShadowTexGenOperator)
    bpy.utils.unregister_class(EditorPanel)
    bpy.utils.unregister_class(CleanOperator)
    bpy.utils.unregister_class(SDFMaterialUpdateOperator)
    del bpy.types.Scene.SdfProperties
    bpy.utils.unregister_class(SdfProperties)
    bpy.utils.unregister_class(SDFTextures)
