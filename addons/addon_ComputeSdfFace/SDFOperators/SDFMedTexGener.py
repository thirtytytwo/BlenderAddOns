import bpy
import os
import math

from mathutils import Vector

class SDFMedTexGenOperator(bpy.types.Operator):
    bl_idname = "object.sdf_med_gen"
    bl_label = "SDFMedTexGenOperator"

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
        
        upVec = rightVec.cross(frontVec)
        return frontVec, rightVec, upVec
        
    def execute(self, context):
        obj = context.selected_objects[0]
        if not obj or not obj.data.uv_layers.active:
            self.report({'ERROR'}, "No active object with UV map found")
            return {'CANCELLED'}
        
        prop = context.scene.SdfProperties
        if not prop:
            self.report({'ERROR'}, "No SdfProperties found")
            return {'CANCELLED'}
        cyclesFlag = False
        if bpy.context.scene.render.engine != 'CYCLES':
            cyclesFlag = True
            bpy.context.scene.render.engine = 'CYCLES'

        #Shader地址
        addonDir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        shaderPath = os.path.join(addonDir, "Shaders", "TestNode.osl")
        print(addonDir)

        # 生成sdf generate 材质
        mat = bpy.data.materials.new(name="SDFMaterial")
        mat.use_nodes = True
        
        #绑定到object上
        originMat = None
        needRemoveSlotFlag = False
        if len(obj.material_slots) == 0:
            needRemoveSlotFlag = True
            bpy.ops.object.material_slot_add()
            obj.material_slots[0].material = mat
        else:
            originMat = obj.material_slots[0].material
            obj.material_slots[0].material = mat
        
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        #清空
        nodes.clear()
        prop.GeneratedTextures.clear()
        
        #生成节点
        outputTexNode = nodes.new(type = 'ShaderNodeTexImage')
        preTexNode = nodes.new(type = 'ShaderNodeTexImage')
        sdfComputeNode = nodes.new(type = 'ShaderNodeScript')
        geometryNode = nodes.new(type = 'ShaderNodeNewGeometry')
        outputNode = nodes.new(type = 'ShaderNodeOutputMaterial')
        lightDirNode = nodes.new(type = "ShaderNodeCombineXYZ")
        
        sdfComputeNode.mode = 'EXTERNAL'
        sdfComputeNode.filepath = bpy.path.abspath(shaderPath)
        sdfComputeNode.update()
        
        #链接节点
        links.new(geometryNode.outputs['Normal'], sdfComputeNode.inputs[0])
        links.new(lightDirNode.outputs['Vector'], sdfComputeNode.inputs[1])
        links.new(sdfComputeNode.outputs['FragColor'], outputNode.inputs['Surface'])
        
        #设置节点属性
        outputTexNode.select = True
        angleStep = 180 / prop.Iterations
        frontVec, rightVec, upVec = self.GetRotationVector(prop)
        lightDirNode.inputs[0].default_value = rightVec.x
        lightDirNode.inputs[1].default_value = rightVec.y
        lightDirNode.inputs[2].default_value = rightVec.z
        outputTexNode.interpolation = 'Closest'
        preTexNode.interpolation = 'Closest'
        outputTexNode.extension = 'CLIP'
        preTexNode.extension = 'CLIP'
        
        #第0次特殊处理
        image = bpy.data.images.new("SDFTexture0", width=int(prop.Resolution), height=int(prop.Resolution))
        prop.GeneratedTextures.add().image = image
        outputTexNode.image = image
        outputTexNode.select = True
        bpy.ops.object.bake(type='EMIT', pass_filter={'COLOR'}, use_clear=True)
        
        #当存在pre了，链接node
        links.new(preTexNode.outputs['Color'], sdfComputeNode.inputs[2])
        
        for i in range(1, prop.Iterations):
            angleDeg = i * angleStep
            angleRad = math.radians(angleDeg)
            
            lightVec = rightVec * math.cos(angleRad) + frontVec * math.sin(angleRad)
        
            lightVec.normalize()
            
            lightDirNode.inputs[0].default_value = lightVec.x
            lightDirNode.inputs[1].default_value = lightVec.y
            lightDirNode.inputs[2].default_value = lightVec.z
            
            preTexNode.image = image
            image = bpy.data.images.new("SDFTexture" + str(i), width=int(prop.Resolution), height=int(prop.Resolution))
            prop.GeneratedTextures.add().image = image
            outputTexNode.image = image
            outputTexNode.select = True
            bpy.ops.object.bake(type='EMIT', pass_filter={'COLOR'}, use_clear=True)
        
        #结束时还原
        bpy.data.materials.remove(mat)
        if needRemoveSlotFlag:
            bpy.ops.object.material_slot_remove()
        else:
            obj.material_slots[0].material = originMat
        
        if cyclesFlag:
            bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
        
        return {"FINISHED"}

