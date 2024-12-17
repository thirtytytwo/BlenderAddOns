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
from .SDFOperators import SdfTextureGenerator
from .SDFPanels import ComputeSdfFacePanel
from .Props import SdfProperties

def register(): 
    bpy.utils.register_class(SdfProperties)
    bpy.types.Scene.SdfProperties = bpy.props.PointerProperty(type=SdfProperties)
    bpy.utils.register_class(SdfTextureGenerator.SdfTextureGenerateOperator)
    bpy.utils.register_class(ComputeSdfFacePanel.ComputeSdfFacePanel)


def unregister(): 
    bpy.utils.unregister_class(SdfTextureGenerator.SdfTextureGenerateOperator)
    bpy.utils.unregister_class(ComputeSdfFacePanel.ComputeSdfFacePanel)
    del bpy.types.Scene.SdfProperties
    bpy.utils.unregister_class(SdfProperties)
