# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from .SDFOperators.SDFMedTexGener import SDFMedTexGenOperator
from .SDFOperators.SDFRetTexGener import SDFRetTexGenOperator
from .SDFOperators.SDFRetTexGenerGPU import SDFRetTexGenGPUOperator
from .SDFPanels.ComputeSdfFacePanel import EditorPanel
from .PluginProps import SDFTextures, SdfProperties

def register(): 
    bpy.utils.register_class(SDFTextures)
    bpy.utils.register_class(SdfProperties)
    bpy.utils.register_class(SDFRetTexGenGPUOperator)
    bpy.types.Scene.SdfProperties = bpy.props.PointerProperty(type=SdfProperties)
    bpy.utils.register_class(SDFMedTexGenOperator)
    bpy.utils.register_class(SDFRetTexGenOperator)
    bpy.utils.register_class(EditorPanel)


def unregister(): 
    bpy.utils.unregister_class(SDFMedTexGenOperator)
    bpy.utils.unregister_class(SDFRetTexGenOperator)
    bpy.utils.unregister_class(SDFRetTexGenGPUOperator)
    bpy.utils.unregister_class(EditorPanel)
    del bpy.types.Scene.SdfProperties
    bpy.utils.unregister_class(SdfProperties)
    bpy.utils.unregister_class(SDFTextures)
