import bpy
from .SDFUtilities import SDFUtilities
from mathutils import Vector

class FaceClampTexGenOperator(bpy.types.Operator):
    bl_idname = "object.face_clamp_gen"
    bl_label = "FaceClampTexGenOperator"

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.selected_objects[0].type == 'MESH'
    
    def GetRotationVector(self, prop):
        axisVector = {
        '+X': Vector((1, 0, 0)),
        '+Y': Vector((0, 1, 0)), 
        '+Z': Vector((0, 0, 1)),
        '-X': Vector((-1, 0, 0)),
        '-Y': Vector((0, -1, 0)),
        '-Z': Vector((0, 0, -1))}
        
        frontVec = axisVector[prop.FaceFront]
        rightVec = axisVector[prop.FaceRight]
        
        return frontVec, rightVec
        
    def execute(self, context):
        props = context.scene.SdfProperties
        size = int(props.Resolution)
        iterations = int(props.Iterations)
        mesh = context.selected_objects[0].data
        
        frontVec, rightVec = self.GetRotationVector(props)
        textures = SDFUtilities.GenSDFMedTexture(mesh, size, iterations, frontVec, rightVec)
        
        for tex in props.FaceClampTextures:
            if tex.image is not None:
                bpy.data.images.remove(tex.image)
        
        props.FaceClampTextures.clear()
        for i in range(len(textures)):
            image = bpy.data.images.new("SDFMedTex" + str(i), width=size, height=size)
            ret = textures[i].read()
            ret.dimensions = size * size * 4
            image.pixels = [v for v in ret]
            image.update()
            props.FaceClampTextures.add().image = image
        
        return {"FINISHED"}

