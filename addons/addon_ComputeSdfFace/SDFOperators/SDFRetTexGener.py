import concurrent.futures
import math
import time
import numpy as np
import bpy
import copy

class Point:
    def __init__(self, dx, dy):
        self.dx = int(dx)
        self.dy = int(dy)
        self.distance = dx * dx + dy * dy

def ComputeSDF(data, width, height):
    res = max(width, height)
    
    grid1 = [[Point(0, 0) for x in range(width + 2)] for y in range(height + 2)]
    grid2 = [[Point(0, 0) for x in range(width + 2)] for y in range(height + 2)]
    
    for y in range(-1, height + 1):
        for x in range(-1, width + 1):
            if x < 0 or y < 0 or x >= width or y >= height:
                grid1[y + 1][x + 1] = Point(res, res)
                grid2[y + 1][x + 1] = Point(res, res)
                continue
            if data[(y * width + x)] < 0.5:
                grid1[y + 1][x + 1] = Point(0, 0)
                grid2[y + 1][x + 1] = Point(res, res)
            else:
                grid1[y + 1][x + 1] = Point(res, res)
                grid2[y + 1][x + 1] = Point(0, 0)
    
    ComputeGrid(grid1, height, width)
    ComputeGrid(grid2, height, width)
    
    ret = []
    for y in range(1, height + 1):
        for x in range(1, width + 1):
            ret.append(ComputePixel(grid1, grid2, x, y))
    return ret

def ComputePixel(grid1, grid2, x, y):
    d1 = int(math.sqrt(float(grid1[y][x].distance)))
    d2 = int(math.sqrt(float(grid2[y][x].distance)))
    dist = d1 - d2
    val = dist * 2 + 128
    if val < 0: val = 0
    if val > 255: val = 255
    
    return val / 255.0

def Compare(grid, point, x, y, offsetX, offsetY):
    temp = grid[y + offsetY][x + offsetX]
    dx = temp.dx + offsetX
    dy = temp.dy + offsetY
    dist = dx * dx + dy * dy

    if dist < point.distance:
        point.dx = dx
        point.dy = dy
        point.distance = dist

def CompareSIMD(data, prevDist):
    dist = np.add(np.multiply(data[:4], data[:4]), np.multiply(data[4:], data[4:]))
    index = int(-1)
    
    for i in range(4):
        if dist[i] < prevDist:
            prevDist = dist[i]
            index = i
    return index

def ComputeGrid(grid, height, width):
    for i in range(height):
        y = i + 1
        for j in range(width):
            x = j + 1
            point = grid[y][x]
            data = np.array([point.dx - 1, point.dx, point.dx - 1, point.dx + 1,
                    point.dy, point.dy - 1, point.dy - 1, point.dy - 1], dtype=np.float32)
            dist = point.distance
            index = CompareSIMD(data, dist)
            if index != -1 :
                point.dx = data[index] 
                point.dy = data[index + 4]
                point.distance = data[index] * data[index] + data[index + 4] * data[index + 4]
        
        for j in range(width - 1, -1, -1):
            x = j + 1
            point = grid[y][x]
            Compare(grid, point, x, y, 1, 0)
            
    for i in range(height - 1, -1, -1):
        y = i + 1
        for j in range(width - 1, -1, -1):
            x = j + 1
            point = grid[y][x]
            data = np.array([point.dx + 1, point.dx, point.dx - 1, point.dx + 1,
                    point.dy, point.dy + 1, point.dy + 1, point.dy + 1], dtype=np.float32)
            dist = point.distance
            index = CompareSIMD(data, dist)
            if index != -1 :
                point.dx = data[index] 
                point.dy = data[index + 4]
                point.distance = data[index] * data[index] + data[index + 4] * data[index + 4]

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
            color_data = np.zeros((height, width, 4), dtype=np.float32)
            color_data[:, :, :3] = ret
            color_data[:, 3] = 1.0  # Alpha
            image.pixels.foreach_set(color_data.ravel())
            image.update()
        endTime = time.time()
        print(f"操作 耗时: {(endTime - startTime):.2f} 秒")
        return {"FINISHED"}