from .SDFMaterialUpdater import update_node_values
import bpy

class CleanOperator(bpy.types.Operator):
    bl_idname = "object.sdf_face_clean"
    bl_label = "FaceTexsCleaner"

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.selected_objects[0].type == 'MESH'
    
    def execute(self, context):
        props = context.scene.SdfProperties
        if len(props.FaceClampTextures) > 0:
            for tex in props.FaceClampTextures:
                if tex.image is not None:
                    bpy.data.images.remove(tex.image)
        props.FaceClampTextures.clear()

        if props.GeneratedTexture is not None:
            bpy.data.images.remove(props.GeneratedTexture)
        props.GeneratedTexture = None

        if props.PreviewActive:
            bpy.app.timers.unregister(update_node_values)
        props.PreviewActive = False
        return {"FINISHED"}

