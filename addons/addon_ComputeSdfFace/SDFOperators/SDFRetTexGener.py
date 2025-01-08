import math
import time
import numpy as np
import bpy


def ComputeSDF(data, width, height):
    res = max(width, height)
    
    grid1 = [[[0,0,0] for x in range(width + 2)] for y in range(height + 2)]
    grid2 = [[[0,0,0] for x in range(width + 2)] for y in range(height + 2)]
    
    for y in range(-1, height + 1):
        for x in range(-1, width + 1):
            if x < 0 or y < 0 or x >= width or y >= height:
                grid1[y + 1][x + 1] = [res,res,res * res]
                grid2[y + 1][x + 1] = [res,res,res * res]
                continue
            elif data[(y * width + x)] < 0.5:
                grid1[y + 1][x + 1] = [0,0,0]
                grid2[y + 1][x + 1] = [res,res,res * res]
            else:
                grid1[y + 1][x + 1] = [res,res,res * res]
                grid2[y + 1][x + 1] = [0,0,0]
    
    ComputeGrid(grid1, height, width)
    ComputeGrid(grid2, height, width)
    
    ret = []
    for y in range(1, height + 1):
        for x in range(1, width + 1):
            ret.append(ComputePixel(grid1, grid2, x, y))
    return ret

def ComputePixel(grid1, grid2, x, y):
    d1 = int(math.sqrt(float(grid1[y][x][2])))
    d2 = int(math.sqrt(float(grid2[y][x][2])))
    dist = d1 - d2
    val = dist * 2 + 128
    if val < 0: val = 0
    if val > 255: val = 255
    
    return val / 255.0

def Compare(grid, point, x, y, offsetX, offsetY):
    temp = grid[y + offsetY][x + offsetX]
    dx = temp[0] + offsetX
    dy = temp[1] + offsetY
    dist = dx * dx + dy * dy

    if dist < point[2]:
        point[0] = dx
        point[1] = dy
        point[2] = dist

def CompareSIMD(grid, x, y, offsets, point):
    
    #TODO：这里读取数据太费了
    offPoints = [grid[y + offsets[i+4]][x + offsets[i]] for i in range(0, 4)]
    
    data = np.array([offPoints[0][0], offPoints[1][0], offPoints[2][0], offPoints[3][0],
                    offPoints[0][1], offPoints[1][1], offPoints[2][1], offPoints[3][1]], dtype=np.int32)
    data = np.add(data, offsets)
    dist = np.add(np.multiply(data[:4], data[:4]), np.multiply(data[4:], data[4:]))
    index = int(-1)
    prevDist = point[2]
    for i in range(4):
        if dist[i] < prevDist:
            prevDist = dist[i]
            index = i
    if index != -1:
        point[0] = data[index]
        point[1] = data[index + 4]
        point[2] = prevDist

def ComputeGrid(grid, height, width):
    for i in range(height):
        y = i + 1
        for j in range(width):
            x = j + 1
            point = grid[y][x]
            offsets = np.array([-1, 0, -1, 1, 0, -1, -1, -1], dtype=np.int8)
            CompareSIMD(grid, x, y, offsets, point)
            
        for j in range(width - 1, -1, -1):
            x = j + 1
            point = grid[y][x]
            Compare(grid, point, x, y, 1, 0)
            
    for i in range(height - 1, -1, -1):
        y = i + 1
        for j in range(width - 1, -1, -1):
            x = j + 1
            point = grid[y][x]
            offsets = np.array([1, 0, -1, 1, 0, 1, 1, 1], dtype=np.int8)
            CompareSIMD(grid, x, y, offsets, point)

        for j in range(width):
            x = j + 1
            point = grid[y][x]
            Compare(grid, point, x, y, -1, 0)


class SDFRetTexGenOperator(bpy.types.Operator):
    bl_idname = "object.sdf_ret_gen"
    bl_label = "SDFRetTexGenOperator"
    
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.selected_objects[0].type == 'MESH'
    
    def execute(self, context):
        props = context.scene.SdfProperties
        startTime = time.time()
        for prop in props.GeneratedTextures:
            image = prop.image
            height = image.size[1]
            width = image.size[0]
            array = np.array(image.pixels[:], dtype=np.float32).reshape(width, height, 4)
            data = array[:, :, 0].flatten()
            ret = ComputeSDF(data, width, height)
            new_pixels = np.zeros((width * height * 4), dtype=np.float32)
            for i in range(height):
                for j in range(width):
                    idx = (i * width + j) * 4
                    new_pixels[idx] = ret[i * width + j]  # R
                    new_pixels[idx + 1] = ret[i * width + j]  # G
                    new_pixels[idx + 2] = ret[i * width + j]  # B
                    new_pixels[idx + 3] = array[i, j, 3]  # A (keep original alpha)
            image.pixels = new_pixels
            image.update()
        endTime = time.time()
        print(f"操作 耗时: {(endTime - startTime):.2f} 秒")
        return {"FINISHED"}