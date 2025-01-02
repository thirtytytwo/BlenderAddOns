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
    
    def GetDistance(self):
        return int(self.dx * self.dx + self.dy * self.dy)

def ComputeSDF(data, width, height):
        res = max(width, height)
        
        grid1 = [[Point(0, 0) for x in range(width + 2)] for y in range(height + 2)]
        grid2 = [[Point(0, 0) for x in range(width + 2)] for y in range(height + 2)]
        
        for y in range(-1, height + 1):
            for x in range(-1, width + 1):
                if x < 0 or y < 0 or x == width or y == height:
                    grid1[y + 1][x + 1] = Point(res, res)
                    grid2[y + 1][x + 1] = Point(res, res)
                    continue
                if data[(y * width + x)] < 0.5:
                    grid1[y + 1][x + 1] = Point(0, 0)
                    grid2[y + 1][x + 1] = Point(res, res)
                else:
                    grid1[y + 1][x + 1] = Point(res, res)
                    grid2[y + 1][x + 1] = Point(0, 0)

        #TODO 这里没有依赖关系，可以用两个线程做
        startTime = time.time()
        # with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        #     futures = []
        #     futures.append(executor.submit(ComputeGrid, grid1, height, width))
        #     futures.append(executor.submit(ComputeGrid, grid2, height, width))
            
        #     for future in concurrent.futures.as_completed(futures):
        #         future.result()
        ComputeGrid(grid1, height, width)
        ComputeGrid(grid2, height, width)
        endTime = time.time()
        print(f"ComputeGrid 耗时: {(endTime - startTime):.2f} 秒")
        #TODO 这里没有依赖关系，可以用多线程
        startTime = time.time() 
        ret = []
        for y in range(1, height + 1):
            for x in range(1, width + 1):
                ret.append(ComputePixel(grid1, grid2, x, y))
        endTime = time.time()
        print(f"ComputePixel 耗时: {(endTime - startTime):.2f} 秒")
        return ret

def ComputePixel(grid1, grid2, x, y):
    d1 = int(math.sqrt(float(grid1[y][x].GetDistance())))
    d2 = int(math.sqrt(float(grid2[y][x].GetDistance())))
    dist = d1 - d2
    val = dist * 2 + 128
    if val < 0: val = 0
    if val > 255: val = 255
    
    return val

def Compare(grid, point, x, y, offsetX, offsetY):
    temp = copy.copy(grid[y + offsetY][x + offsetX])
    temp.dx += offsetX
    temp.dy += offsetY

    if temp.GetDistance() < point.GetDistance():
        point.dx = temp.dx
        point.dy = temp.dy

def CompareSIMD(data, prevDist):
    distX = np.multiply(data[:4], data[:4])
    distY = np.multiply(data[4:], data[4:])
    dist = np.add(distX, distY)
    index = int(-1)
    
    for i in range(4):
        if dist[i] < prevDist:
            prevDist = dist[i]
            index = i
    return index

def ComputeGrid(grid, height, width):
        for i in range(height):
            for j in range(width):
                x = j + 1
                y = i + 1
                point = grid[y][x]
                data = np.array([point.dx - 1, point.dx, point.dx - 1, point.dx + 1,
                        point.dy, point.dy - 1, point.dy - 1, point.dy - 1], dtype=np.int32)
                
                index = CompareSIMD(data, point.GetDistance())
                if index != -1 :
                    point.dx = data[index] 
                    point.dy = data[index + 4]
                # Compare(grid, point, x, y, -1, -1)
                # Compare(grid, point, x, y, 0, -1)
                # Compare(grid, point, x, y, 1, -1)
                # Compare(grid, point, x, y, -1, 0)
            for j in range(width - 1, -1, -1):
                x = j + 1
                point = grid[y][x]
                Compare(grid, point, x, y, 1, 0)
                
        for i in range(height - 1, -1, -1):
            for j in range(width - 1, -1, -1):
                x = j + 1
                y = i + 1
                point = grid[y][x]
                data = np.array([point.dx + 1, point.dx, point.dx - 1, point.dx + 1,
                        point.dy, point.dy + 1, point.dy + 1, point.dy + 1], dtype=np.int32)
                
                index = CompareSIMD(data, point.GetDistance())
                if index != -1 :
                    point.dx = data[index] 
                    point.dy = data[index + 4]
                
                # Compare(grid, point, x, y, 1, 1)
                # Compare(grid, point, x, y, 0, 1)
                # Compare(grid, point, x, y, -1, 1)
                # Compare(grid, point, x, y, 1, 0)
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
        # images = []
        # for tex in props.GeneratedTextures:
        #     images.append(tex.image)
        
        image = props.GeneratedTextures[0].image
        array = np.array(image.pixels[:], dtype=np.float32).reshape(image.size[1], image.size[0], 4)
        data = array[:, :, 0].flatten()
        
        startTime = time.time()
        ret = ComputeSDF(data, image.size[0], image.size[1])
        endTime = time.time()
        print(f"ComputeSDF 耗时: {(endTime - startTime):.2f} 秒")
        
        # for y in range(image.size[1]):
        #     for x in range(image.size[0]):
        #         index = (y * image.size[0] + x) * 4
        #         val = ret[y * image.size[0] + x] / 255.0
        #         image.pixels[index] = val
        #         image.pixels[index + 1] = val
        #         image.pixels[index + 2] = val
        #         image.pixels[index + 3] = 1.0
        # image.update()

        # with concurrent.futures.ThreadPoolExecutor(max_workers = len(images)) as executor:
        #     futures = []
        #     for image in images:
        #         array = np.array(image.pixels[:], dtype=np.float32).reshape(image.size[1], image.size[0], 4)
        #         data = array[:, :, 0].flatten()
        #         futures.append(executor.submit(ComputeSDF, data, image.size[0], image.size[1]))
            
        #     for future in concurrent.futures.as_completed(futures):
        #         temp = []
        #         temp = future.result()
        #         print(1)
        
        return {"FINISHED"}