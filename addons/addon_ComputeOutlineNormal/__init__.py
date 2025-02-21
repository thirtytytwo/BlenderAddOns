import bpy

from .operators.AddonOperators import ComputeOutlineNormalOperator
from .operators.ModifyMeshVertex import ModifyMeshVertexOperator
from .panels.AddonPanels import ComputeOutlineNormalPanel


def register():
    bpy.utils.register_class(ComputeOutlineNormalOperator)
    bpy.utils.register_class(ModifyMeshVertexOperator)
    bpy.utils.register_class(ComputeOutlineNormalPanel)

def unregister():
    bpy.utils.unregister_class(ComputeOutlineNormalOperator)
    bpy.utils.unregister_class(ModifyMeshVertexOperator)
    bpy.utils.unregister_class(ComputeOutlineNormalPanel)