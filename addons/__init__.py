import bpy

from .AddonOperators import ComputeOutlineNormalOperator

bl_info = {
    "name": "Move X Axis",
    "blender": (3, 6, 0),
    "category": "Object",
}

def menu_func(self, context):
    self.layout.operator(ComputeOutlineNormalOperator.bl_idname)

def register():
    bpy.utils.register_class(ComputeOutlineNormalOperator)
    bpy.types.VIEW3D_MT_object.append(menu_func)  # Adds the new operator to an existing menu.

def unregister():
    bpy.utils.unregister_class(ComputeOutlineNormalOperator) # removes
