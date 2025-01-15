import numpy as np
import bpy
import gpu
import gpu_extras.batch
import os

def GetMainLogicShaderInfo():
    shaderInfo = gpu.types.GPUShaderCreateInfo()
    #插入顶点着色器和片段着色器
    addonDir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    vertPath = os.path.join(addonDir, "Shaders", "FullScreenVert.glsl")
    fragPath = os.path.join(addonDir, "Shaders", "JFSdfFrag.glsl")
    with open(vertPath, "r", encoding="utf-8") as f:
        shaderInfo.vertex_source(f.read())
    with open(fragPath, "r", encoding="utf-8") as f:
        shaderInfo.fragment_source(f.read())
    #设置输入输出
    shaderInfo.vertex_in(0, 'VEC3', 'position')
    shaderInfo.vertex_in(1, 'VEC2', 'uv')
    vertOut = gpu.types.GPUStageInterfaceInfo("OUTPUT")
    vertOut.smooth('VEC2', 'uvInterp')
    shaderInfo.vertex_out(vertOut)
    
    shaderInfo.sampler(0, 'FLOAT_2D', "ImageInput")
    shaderInfo.fragment_out(0, 'VEC4', 'FragColor')
    #设置常量
    shaderInfo.push_constant('FLOAT', 'sampleStep')
    return shaderInfo

def GetPreLogicShaderInfo():
    shaderInfo = gpu.types.GPUShaderCreateInfo()
    #插入顶点着色器和片段着色器
    addonDir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    vertPath = os.path.join(addonDir, "Shaders", "FullScreenVert.glsl")
    fragPath = os.path.join(addonDir, "Shaders", "01ToUVFrag.glsl")
    with open(vertPath, "r", encoding="utf-8") as f:
        shaderInfo.vertex_source(f.read())
    with open(fragPath, "r", encoding="utf-8") as f:
        shaderInfo.fragment_source(f.read())
    #设置输入输出
    shaderInfo.vertex_in(0, 'VEC3', 'position')
    shaderInfo.vertex_in(1, 'VEC2', 'uv')
    vertOut = gpu.types.GPUStageInterfaceInfo("OUTPUT")
    vertOut.smooth('VEC2', 'uvInterp')
    shaderInfo.vertex_out(vertOut)
    
    shaderInfo.sampler(0, 'FLOAT_2D', "ImageInput")
    shaderInfo.fragment_out(0, 'VEC4', 'FragColor')
    return shaderInfo

def GetLastLogicShaderInfo():
    shaderInfo = gpu.types.GPUShaderCreateInfo()
    #插入顶点着色器和片段着色器
    addonDir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    vertPath = os.path.join(addonDir, "Shaders", "FullScreenVert.glsl")
    fragPath = os.path.join(addonDir, "Shaders", "UVFragTo01.glsl")
    with open(vertPath, "r", encoding="utf-8") as f:
        shaderInfo.vertex_source(f.read())
    with open(fragPath, "r", encoding="utf-8") as f:
        shaderInfo.fragment_source(f.read())
    #设置输入输出
    shaderInfo.vertex_in(0, 'VEC3', 'position')
    shaderInfo.vertex_in(1, 'VEC2', 'uv')
    vertOut = gpu.types.GPUStageInterfaceInfo("OUTPUT")
    vertOut.smooth('VEC2', 'uvInterp')
    shaderInfo.vertex_out(vertOut)
    
    shaderInfo.sampler(0, 'FLOAT_2D', "ImageInput")
    shaderInfo.fragment_out(0, 'VEC4', 'FragColor')
    return shaderInfo

def add_01_to_image_pixels(image):
    size = image.size[0]
    
    texture = gpu.texture.from_image(image)
    
    preShader = gpu.shader.create_from_info(GetPreLogicShaderInfo())
    mainShader = gpu.shader.create_from_info(GetMainLogicShaderInfo())
    lastShader = gpu.shader.create_from_info(GetLastLogicShaderInfo())
    #设置网格batch
    vertices = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    tex_coords = [(0, 0), (1, 0), (1, 1), (0, 1)]
    indices = [(0, 1, 2), (2, 3, 0)]
    #绑定网格batch
    preBatch = gpu_extras.batch.batch_for_shader(preShader, 'TRIS', {"position" : vertices, "uv" : tex_coords}, indices=indices)
    mainBatch = gpu_extras.batch.batch_for_shader(mainShader, 'TRIS', {"position" : vertices, "uv" : tex_coords}, indices=indices)
    lastBatch = gpu_extras.batch.batch_for_shader(lastShader, 'TRIS', {"position" : vertices, "uv" : tex_coords}, indices=indices)
    
    #在主逻辑之前，尝试把颜色为一的赋值他的uv
    offScreen = gpu.types.GPUOffScreen(size, size, format = 'RGBA32F')
    with offScreen.bind():
        preShader.bind()
        preShader.uniform_sampler("ImageInput", texture)
        preBatch.draw(preShader)
        texture = offScreen.texture_color
    offScreen.free()
    index = size // 2
    while index >= 1:
        offScreen = gpu.types.GPUOffScreen(size, size, format = 'RGBA32F')
        with offScreen.bind():
            mainShader.bind()
            mainShader.uniform_float("sampleStep", index/size)
            mainShader.uniform_sampler("ImageInput", texture)
            mainBatch.draw(mainShader)
            texture = offScreen.texture_color
        offScreen.free()
        index //= 2
    
    offScreen = gpu.types.GPUOffScreen(size, size, format = 'RGBA32F')
    with offScreen.bind():
        lastShader.bind()
        lastShader.uniform_sampler("ImageInput", texture)
        lastBatch.draw(lastShader)
        texture = offScreen.texture_color
    offScreen.free()
    
    return texture.read()



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