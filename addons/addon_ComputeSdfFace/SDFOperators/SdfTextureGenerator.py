import bpy
import os
import math

from mathutils import Vector

class SdfTextureGenerateOperator(bpy.types.Operator):
    bl_idname = "object.sdf_texturegenerate"
    bl_label = "SdfTextureGenerator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        obj = context.active_object
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
        #生成sdf generate 材质
        mat = obj.data.materials.get('SDFMaterial')    
        if not mat:
            mat = bpy.data.materials.new(name='SDFMaterial')
            obj.data.materials.append(mat)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        nodes.clear()
        
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
        
        #设置节点
        links.new(geometryNode.outputs['Normal'], sdfComputeNode.inputs[0])
        links.new(lightDirNode.outputs['Vector'], sdfComputeNode.inputs[1])
        links.new(preTexNode.outputs['Color'], sdfComputeNode.inputs[2])
        links.new(sdfComputeNode.outputs['FragColor'], outputNode.inputs['Surface'])
        
        #预先选定输出图片节点
        outputTexNode.select = True
        
        #根据插值设置循环
        angleStep = 180 / prop.Iterations
        image = bpy.data.images.new("SDFTexture0", width=int(prop.Resolution), height=int(prop.Resolution))
        prop.GeneratedTextures.add(image)
        for i in range(prop.Iterations):
            angleDeg = i * angleStep
            angleRad = math.radians(angleDeg)
            
            x = math.cos(angleRad)
            y = math.sin(angleRad)
            z = 0
            
            lightVec = Vector((x, y, z))
            lightVec.normalize()
            
            print(lightVec)
            lightDirNode.inputs[0].default_value = lightVec.x
            lightDirNode.inputs[1].default_value = lightVec.y
            lightDirNode.inputs[2].default_value = lightVec.z
            
            # if i == 0:
            #     bpy.ops.object.bake(type='EMIT', pass_filter={'COLOR'}, use_clear=True)
        # # Set bake settings
        # image = bpy.data.images.new("Baked_Texture", width=512, height=512)
        # bpy.context.scene.render.engine = 'CYCLES'
        
        # # Select the object and set it active
        # bpy.ops.object.select_all(action='DESELECT')
        # obj.select_set(True)
        # bpy.context.view_layer.objects.active = obj
        
        # # Bake the image
        # texNode = nodes.new(type='ShaderNodeTexImage')
        # texNode.image = image
        # bpy.ops.object.bake(type='EMIT', pass_filter={'COLOR'})
        
        # # Save the baked image
        # image.filepath_raw = "C:\\Users\\xy\\Desktop\\material002_bake.png"
        # image.file_format = 'PNG'
        # image.save()
        # print("Baked image saved to", image.filepath_raw)
        
        #结束时还原设置
        if cyclesFlag:
            bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        
        return {"FINISHED"}

