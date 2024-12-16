import bpy

class SDFOperator(bpy.types.Operator):
    bl_idname = "object.sdf"
    bl_label = "SDFOperator"

    def execute(self, context):
        return {"FINISHED"}

