import time
import numpy as np
import bpy
import ctypes
import os
from .SDFUtilities import SDFUtilities

class FaceShadowTexGenOperator(bpy.types.Operator):
    bl_idname = "object.face_shadow_gen"
    bl_label = "FaceShadowTexGenOperator"
    
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.selected_objects[0].type == 'MESH'
    
    def execute(self, context):
        props = context.scene.SdfProperties
        size = int(props.Resolution)
        
        computeRet = []
        clampTexs = []
        index = 0
        addonDir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        dllPath = os.path.join(addonDir, "DLLs", "ComputeSDF.dll")
        lib = ctypes.CDLL(dllPath)
        lib.ComputeSDF.argtypes = [ctypes.c_int, np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS')]
        lib.ComputeSDF.restype = ctypes.POINTER(ctypes.c_float)
        
        arrays = []
        for prop in props.FaceClampTextures:
            if prop.image is None: return {"FINISHED"}
            startTime = time.time()
            image = prop.image
            clampTexs.append(image)
            
            data = np.array(image.pixels[:], dtype=np.float32).reshape(size, size, 4)
            data = data[:, :, 0].flatten()

            resultPtr = lib.ComputeSDF(size, data)
            resultData = np.ctypeslib.as_array(resultPtr, shape=(size * size,)).copy()
            arrays.append(resultData)
            
            elapsedTime = time.time() - startTime
            print(f"逻辑运行时间: {elapsedTime:.2f} 秒")

            startTime = time.time()
            pixelData = np.zeros(size * size * 4, 'f')
            pixelData[0::4] = resultData[:]
            pixelData[1::4] = resultData[:]
            pixelData[2::4] = resultData[:]
            pixelData[3::4] = 1.0
            
            #TODO 需要确定一下image是否需要使用new这个方法，可以有其他的内部图片申请吗
            image = bpy.data.images.new("SDFComputeTex" + str(index), width=size, height=size)
            image.pixels = pixelData
            image.update()
            computeRet.append(image)
            index += 1
            elapsedTime = time.time() - startTime
            print(f"应用结果数据时间: {elapsedTime:.2f} 秒")
        data = SDFUtilities.SDFCombineToFaceTexture(computeRet, size, True)
        if data != None:
            if props.GeneratedTexture is None:
                image = bpy.data.images.new("SDFRet", width=size, height=size)
                data.dimensions = size * size * 4
                image.pixels = [v for v in data]
                image.update()
                props.GeneratedTexture = image
            else:
                data.dimensions = size * size * 4
                props.GeneratedTexture.pixels = [v for v in data]
                props.GeneratedTexture.update()
        else:
            self.report({'ERROR'}, "生成SDF图片失败")
        for tex in computeRet:
            bpy.data.images.remove(tex, do_unlink=True)
        return {"FINISHED"}