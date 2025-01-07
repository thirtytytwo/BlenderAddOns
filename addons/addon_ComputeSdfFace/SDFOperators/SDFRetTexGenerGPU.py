import numpy as np
import bpy
import gpu
import gpu_extras.presets
import os
def add_01_to_image_pixels(image):

    size = image.size[0]
    
    inputRT = gpu.texture.from_image(image)
    outputRT = gpu.types.GPUTexture((size, size), format='RGBA32F')
    
    computeShaderInfo = gpu.types.GPUShaderCreateInfo()
    computeShaderInfo.push_constant('FLOAT', 'sampleStep')
    computeShaderInfo.push_constant('FLOAT', 'size')
    
    computeShaderInfo.sampler(0, 'FLOAT_2D', "ImageInput")
    computeShaderInfo.image(1, 'RGBA32F', "FLOAT_2D", "ImageOutput", qualifiers={"WRITE"})
    
    addonDir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    shaderPath = os.path.join(addonDir, "Shaders", "JumpFloodSDF.glsl")
    with open(shaderPath, "r", encoding="utf-8") as f:
        computeShaderInfo.compute_source(f.read())
    computeShaderInfo.local_group_size(1, 1)
    
    # i = size // 2
    # while i >= 1:
    #     computeShader = gpu.shader.create_from_info(computeShaderInfo)
    #     computeShader.uniform_sampler("ImageInput", inputRT)
    #     computeShader.image("ImageOutput", outputRT)
    #     computeShader.uniform_float('sampleStep', i)
    #     computeShader.uniform_float('size', size)
    #     gpu.compute.dispatch(computeShader, size, size, 1)
    #     i //= 2
    #     if i >= 1:
    #         temp = inputRT
    #         inputRT = outputRT
    #         outputRT = temp
    
    computeShader = gpu.shader.create_from_info(computeShaderInfo)
    computeShader.uniform_sampler("ImageInput", inputRT)
    computeShader.image("ImageOutput", outputRT)
    computeShader.uniform_float('size', size)
    computeShader.uniform_float('sampleStep', size // 512)
    gpu.compute.dispatch(computeShader, size, size, 1)
    data = outputRT.read()

    return data



class SDFRetTexGenGPUOperator(bpy.types.Operator):
    bl_idname = "object.sdf_ret_gen_gpu"
    bl_label = "SDFRetTexGenGPUOperator"
    
    
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.selected_objects[0].type == 'MESH'
    
    def execute(self, context):
        props = context.scene.SdfProperties
        
        images = []
        for tex in props.GeneratedTextures:
            images.append(tex.image)
        
        data = add_01_to_image_pixels(images[0])
        data.dimensions = images[0].size[0] * images[0].size[1] * 4
        images[0].pixels = [v for v in data]
        images[0].update()
        
        return {"FINISHED"}