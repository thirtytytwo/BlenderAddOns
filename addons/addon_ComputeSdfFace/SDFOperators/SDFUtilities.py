import math
import os

import numpy as np
import bpy
import gpu
import gpu_extras

def GenMedTexShader():
    shaderInfo = gpu.types.GPUShaderCreateInfo()
    #插入顶点着色器和片段着色器
    addonDir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    vertPath = os.path.join(addonDir, "Shaders", "MedSDFVert.glsl")
    fragPath = os.path.join(addonDir, "Shaders", "MedSDFFrag.glsl")
    with open(vertPath, "r", encoding="utf-8") as f:
        shaderInfo.vertex_source(f.read())
    with open(fragPath, "r", encoding="utf-8") as f:
        shaderInfo.fragment_source(f.read())
    #设置输入输出
    shaderInfo.vertex_in(0, 'VEC3', 'position')
    shaderInfo.vertex_in(1, 'VEC3', 'normal')
    shaderInfo.vertex_in(2, 'VEC2', 'uv')
    vertOut = gpu.types.GPUStageInterfaceInfo("OUTPUT")
    vertOut.smooth('VEC2', 'uvInterp')
    vertOut.smooth('VEC3', 'normalInterp')
    shaderInfo.vertex_out(vertOut)
    
    shaderInfo.sampler(0, 'FLOAT_2D', "ImageInput")
    shaderInfo.fragment_out(0, 'VEC4', 'FragColor')
    #设置常量
    shaderInfo.push_constant('VEC3', 'lightDir')
    shaderInfo.push_constant('FLOAT', 'flag')
    return shaderInfo

def GenCombineShader():
    shaderInfo = gpu.types.GPUShaderCreateInfo()
    #插入顶点着色器和片段着色器
    addonDir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    vertPath = os.path.join(addonDir, "Shaders", "FullScreenVert.glsl")
    fragPath = os.path.join(addonDir, "Shaders", "CombineFrag.glsl")
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
    
    shaderInfo.sampler(0, 'FLOAT_2D', "SDFA")
    shaderInfo.sampler(1, 'FLOAT_2D', "SDFB")
    # shaderInfo.sampler(2, 'FLOAT_2D', "Pre")
    # shaderInfo.push_constant('FLOAT', 'weight')
    # shaderInfo.push_constant('INT', 'flag')
    shaderInfo.fragment_out(0, 'VEC4', 'FragColor')
    return shaderInfo

def GetBatchData(mesh, needNormal = False):
    uvLayer = mesh.uv_layers["Face"]
    vertices = []
    uvs = []
    normals = []
    
    triLoop = mesh.loop_triangles
    for tri in triLoop:
        for loopIndex in tri.loops:
            uv = uvLayer.uv[loopIndex].vector
            if needNormal:
                normal = mesh.loops[loopIndex].normal
                normals.append((float(normal.x), float(normal.y), float(normal.z)))
            vertices.append((float(uv.x), float(uv.y), float(0)))
            uvs.append((float(uv.x), float(uv.y)))
    if needNormal:
        return vertices, uvs, normals
    else:
        return vertices, uvs

class SDFUtilities:
    
    @staticmethod
    def GenSDFMedTexture(mesh, size, iterations, frontVec, rightVec):
        angleStep = 180 / iterations
        vertices, uvs, normals = GetBatchData(mesh, True)
        
        vertices_np = np.array(vertices, dtype=np.float32)
        uvs_np = np.array(uvs, dtype=np.float32)
        normals_np = np.array(normals, dtype=np.float32)
        
        shader = gpu.shader.create_from_info(GenMedTexShader())
        batch = gpu_extras.batch.batch_for_shader(shader, 'TRIS', {"position" : vertices_np, "normal" : normals_np, "uv" : uvs_np})
        
        textures = []
        for i in range(iterations):
            offScreen = gpu.types.GPUOffScreen(size, size, format = 'RGBA32F')
            with offScreen.bind():
                if i == 0:
                    shader.bind()
                    shader.uniform_float("lightDir", rightVec)
                    shader.uniform_float("flag", 0)
                    batch.draw(shader)
                    textures.append(offScreen.texture_color)
                else:
                    angleDeg = i * angleStep
                    angleRad = math.radians(angleDeg)
                    lightVec = rightVec * math.cos(angleRad) + frontVec * math.sin(angleRad)
                    lightVec.normalize()
                    
                    shader.bind()
                    shader.uniform_float("lightDir", lightVec)
                    shader.uniform_float("flag", 1)
                    shader.uniform_sampler("ImageInput", textures[i - 1])
                    batch.draw(shader)
                    textures.append(offScreen.texture_color)
            offScreen.free()
        return textures
        
    @staticmethod
    def SDFCombineToFaceTexture(clampTexs ,computeTexs, size, needToRevert = False):
        
        clampTexs = [gpu.texture.from_image(tex) for tex in clampTexs]
        if needToRevert:
            computeTexs = [gpu.texture.from_image(tex) for tex in computeTexs]
        vertices = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
        indices = [(0, 1, 2), (2, 3, 0)]
        shader = gpu.shader.create_from_info(GenCombineShader())
        batch = gpu_extras.batch.batch_for_shader(shader, 'TRIS', {"position" : vertices, "uv" : uvs}, indices=indices)
        
        texture = None
        offScreen = gpu.types.GPUOffScreen(size, size, format = 'RGBA32F')
        with offScreen.bind():
            
            shader.bind()
            # shader.uniform_float("weight", 1.0 / len(computeTexs))
            shader.uniform_sampler("SDFA", computeTexs[0])
            shader.uniform_sampler("SDFB", computeTexs[1])
            # shader.uniform_int("flag", 0)   
            batch.draw(shader)
            texture = offScreen.texture_color
        offScreen.free()
        # for i in range(2, len(computeTexs)):
        #     print(i)
        #     offScreen = gpu.types.GPUOffScreen(size, size, format = 'RGBA32F')
        #     with offScreen.bind():
        #         shader.bind()
        #         shader.uniform_float("weight", 1.0 / len(computeTexs))
        #         shader.uniform_int("flag", 1)
        #         shader.uniform_sampler("ImageInput", computeTexs[i])
        #         shader.uniform_sampler("Pre", texture)
        #         batch.draw(shader)
        #         texture = offScreen.texture_color
        #     offScreen.free()
        return texture.read()