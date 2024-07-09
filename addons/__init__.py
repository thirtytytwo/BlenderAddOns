import bpy

from .AddonOperators import ComputeOutlineNormalOperator
from .AddonPannel import ComputeOutlineNormalPannel

bl_info = {
    "name": "ComputeOutlineNormal",
    "author": "luyicheng",
    "version":(1,0),
    "blender": (3, 6, 0),
    "description": "for NPR outline feature,  auto calculate smooth normal for outline, and use octahedron to pack datas to two dimension",
    "support":"COMMUNITY",
    "category": "Object"
}

def menu_func(self, context):
    self.layout.operator(ComputeOutlineNormalOperator.bl_idname)

def register():
    bpy.utils.register_class(ComputeOutlineNormalPannel)
    bpy.utils.register_class(ComputeOutlineNormalOperator)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(ComputeOutlineNormalPannel)
    bpy.utils.unregister_class(ComputeOutlineNormalOperator)# removes
