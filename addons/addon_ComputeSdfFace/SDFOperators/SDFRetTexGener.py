import math
import time
import numpy as np
import bpy
import ctypes
from .SDFUtilities import SDFUtilities

def ComputeSDF(data,size):
    
    grid1 = [[(0,0,0) for _ in range(size + 2)] for _ in range(size + 2)]
    grid2 = [[(0,0,0) for _ in range(size + 2)] for _ in range(size + 2)]
    
    for y in range(-1, size + 1):
        for x in range(-1, size + 1):
            if x < 0 or y < 0 or x >= size or y >= size:
                grid1[y + 1][x + 1] = (9999, 9999, 9999 * 9999 + 9999 * 9999)
                grid2[y + 1][x + 1] = (9999, 9999, 9999 * 9999 + 9999 * 9999)
                continue
            elif data[(y * size + x)] > 0.5:
                grid1[y + 1][x + 1] = (0, 0, 0)
                grid2[y + 1][x + 1] = (9999, 9999, 9999 * 9999 + 9999 * 9999)
            else:
                grid1[y + 1][x + 1] = (9999, 9999, 9999 * 9999 + 9999 * 9999)
                grid2[y + 1][x + 1] = (0, 0, 0)
    
    insideMax = ComputeGrid(grid1,size)
    outsideMax = ComputeGrid(grid2,size)
    
    result = []
    for i in range(size):
        for j in range(size):
            dist1 = int(math.sqrt(float(grid1[i + 1][j + 1][2])))
            dist2 = int(math.sqrt(float(grid2[i + 1][j + 1][2])))
            
            dist = (dist1 - dist2)
            c = 0.5
            if dist < 0:
                c += dist / math.sqrt(outsideMax) * 0.5
            else:
                c += dist / math.sqrt(insideMax) * 0.5
            result.append(float(c))
    return result

def ComputeGrid(grid, size):
    offsetBottomLeft = [-1, 0, -1, 1, 0, -1, -1, -1]
    offsetTopRight = [1, 0, -1, 1, 0, 1, 1, 1]
    maxValue = -1
    for i in range(size):
        y = i + 1
        for j in range(size):
            x = j + 1
            flag = False
            point = grid[y][x]
            
            offsetPoints = [grid[y + offsetBottomLeft[i + 4]][x + offsetBottomLeft[i]] for i in range(4)]
            for i in range(4):
                xVal = offsetPoints[i][0] + offsetBottomLeft[i]
                yVal = offsetPoints[i][1] + offsetBottomLeft[i + 4]
                dist = xVal * xVal + yVal * yVal
                if dist < point[2]:
                    flag = True
                    point = (xVal, yVal, dist)
            if flag : grid[y][x] = point
            
        for j in range(size - 1, -1, -1):
            x = j + 1
            p0 = grid[y][x]
            p1 = grid[y][x + 1]
            
            xVal = p1[0] + 1
            yVal = p1[1]
            dist = xVal * xVal + yVal * yVal
            if dist < p0[2]:
                grid[y][x] = (xVal, yVal, dist)
            
            
    for i in range(size - 1, -1, -1):
        y = i + 1
        for j in range(size - 1, -1, -1):
            x = j + 1
            flag = False
            point = grid[y][x]
            
            offsetPoints = [grid[y + offsetTopRight[i + 4]][x + offsetTopRight[i]] for i in range(4)]
            for i in range(4):
                xVal = offsetPoints[i][0] + offsetTopRight[i]
                yVal = offsetPoints[i][1] + offsetTopRight[i + 4]
                dist = xVal * xVal + yVal * yVal
                if dist < point[2]:
                    flag = True
                    point = (xVal, yVal, dist)
            if flag : grid[y][x] = point

        for j in range(size):
            x = j + 1
            p0 = grid[y][x]
            if p0[2] > maxValue:
                maxValue = float(p0[2])
            p1 = grid[y][x-1]
            xVal = p1[0] - 1
            yVal = p1[1]
            dist = xVal * xVal + yVal * yVal
            if dist < p0[2]:
                grid[y][x] = (xVal, yVal,dist)
                
    return maxValue

class ArrayData(ctypes.Structure):
    _fields_ = [("data", ctypes.POINTER(ctypes.c_float)), ("arraySize", ctypes.c_int)]
class SDFData(ctypes.Structure):
    _fields_ = [("sdfs", ctypes.POINTER(ArrayData)), ("sdfArrayNum", ctypes.c_int)]

class SDFRetTexGenOperator(bpy.types.Operator):
    bl_idname = "object.sdf_ret_gen"
    bl_label = "SDFRetTexGenOperator"
    
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.selected_objects[0].type == 'MESH'
    
    def execute(self, context):
        props = context.scene.SdfProperties
        size = int(props.Resolution)
        
        computeRet = []
        clampRet = []
        index = 0
        
        lib = ctypes.CDLL("./DLLs/ComputeSDF.dll")
        lib.ComputeSDF.argtypes = [ctypes.c_int, np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS')]
        lib.ComputeSDF.restype = ctypes.POINTER(ctypes.c_float)
        
        arrays = []
        for prop in props.FaceClampTextures:
            if prop.image is None: return {"FINISHED"}
            startTime = time.time()
            image = prop.image
            clampRet.append(image)
            
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
        data = SDFUtilities.SDFCombineToFaceTexture(clampRet, computeRet, size, True)
        
        # data2c = []
        # for arr in arrays:
        #     data = ArrayData()
        #     data.data = arr.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        #     data.arraySize = arr.size
        #     data2c.append(data)
        
        # arrayNum = len(arrays)
        # data2c1 = (ArrayData * arrayNum)(*data2c)
        # sdfData = SDFData()
        # sdfData.sdfs = data2c1
        # sdfData.sdfArrayNum = arrayNum
        
        if data != None:
            image = bpy.data.images.new("SDFRet", width=size, height=size)
            data.dimensions = size * size * 4
            image.pixels = [v for v in data]
            image.update()

        prop.GeneratedTexture = image
        for tex in computeRet:
            bpy.data.images.remove(tex, do_unlink=True)
        return {"FINISHED"}