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
from .SDFOperators.FaceClampGener import FaceClampTexGenOperator
from .SDFOperators.FaceShadowGener import FaceShadowTexGenOperator
from .SDFOperators.Cleaner import CleanOperator
from .SDFPanels.ComputeSdfFacePanel import EditorPanel
from .PluginProps import SDFTextures, SdfProperties

def register(): 
    bpy.utils.register_class(SDFTextures)
    bpy.utils.register_class(SdfProperties)
    bpy.utils.register_class(CleanOperator)
    bpy.types.Scene.SdfProperties = bpy.props.PointerProperty(type=SdfProperties)
    bpy.utils.register_class(FaceClampTexGenOperator)
    bpy.utils.register_class(FaceShadowTexGenOperator)
    bpy.utils.register_class(EditorPanel)


def unregister(): 
    bpy.utils.unregister_class(FaceClampTexGenOperator)
    bpy.utils.unregister_class(FaceShadowTexGenOperator)
    bpy.utils.unregister_class(EditorPanel)
    bpy.utils.unregister_class(CleanOperator)
    del bpy.types.Scene.SdfProperties
    bpy.utils.unregister_class(SdfProperties)
    bpy.utils.unregister_class(SDFTextures)
