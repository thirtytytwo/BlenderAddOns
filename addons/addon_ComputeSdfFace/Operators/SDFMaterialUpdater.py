import bpy
from .SDFUtilities import SDFUtilities

def update_node_values():
    context = bpy.context
    props = context.scene.SdfProperties
    if not props.PreviewActive:
        return None  # Stop the timer

    obj = context.selected_objects[0]
    material = obj.data.materials[0]

    nodeA = next((node for node in material.node_tree.nodes if node.label == "LightAngle"), None)
    nodeB = next((node for node in material.node_tree.nodes if node.label == "SmoothArea"), None)

    if nodeA:
        nodeA.outputs[0].default_value = props.LightAngle
    if nodeB:
        nodeB.outputs[0].default_value = props.SmoothArea

    return 1.0 / 30  # Repeat the timer every 1/30 seconds

class SDFMaterialUpdateOperator(bpy.types.Operator):
    bl_idname = "object.sdf_face_show_update"
    bl_label = "SDFMaterialUpdater"
    
    def execute(self, context):
        props = context.scene.SdfProperties
        props.PreviewActive = not props.PreviewActive
        if props.PreviewActive:
            obj = context.selected_objects[0]
            SDFUtilities.LoadSDFMaterialAndLink(obj, props.GeneratedTexture)
            bpy.app.timers.register(update_node_values)
        else:
            bpy.app.timers.unregister(update_node_values)
        return {"FINISHED"}