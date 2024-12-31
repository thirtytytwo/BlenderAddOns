import concurrent.futures
import math
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
        
        grid1 = [[Point(0, 0) for x in range(width)] for y in range(height)]
        grid2 = [[Point(0, 0) for x in range(width)] for y in range(height)]
        
        for y in range(height):
            for x in range(width):
                if data[(y * width + x)] < 0.5:
                    grid1[y][x] = Point(0, 0)
                    grid2[y][x] = Point(res, res)
                else:
                    grid1[y][x] = Point(res, res)
                    grid2[y][x] = Point(0, 0)

        #TODO 这里没有依赖关系，可以用两个线程做
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = []
            futures.append(executor.submit(ComputeGrid, grid1, height, width))
            futures.append(executor.submit(ComputeGrid, grid2, height, width))
            
            for future in concurrent.futures.as_completed(futures):
                future.result()

        #TODO 这里没有依赖关系，可以用多线程
        ret = []
        for y in range(height):
            for x in range(width):
                ret.append(ComputePixel(grid1, grid2, x, y))
        return ret

def ComputePixel(grid1, grid2, x, y):
    d1 = int(math.sqrt(float(Get(grid1, x, y).GetDistance())))
    d2 = int(math.sqrt(float(Get(grid2, x, y).GetDistance())))
    dist = d1 - d2
    val = dist * 2 + 128
    if val < 0: val = 0
    if val > 255: val = 255
    
    return val
        
def Get(grid, x, y):
    if x >= 0 and y >=0 and x < len(grid[0]) and y < len(grid):
        return grid[y][x]
    else:
        return Point(len(grid), len(grid))
        
def Compare(grid, point, x, y, offsetX, offsetY):
    temp = copy.copy(Get(grid, x + offsetX, y + offsetY))
    temp.dx += offsetX
    temp.dy += offsetY

    if temp.GetDistance() < point.GetDistance():
        point.dx = temp.dx
        point.dy = temp.dy


def ComputeGrid(grid, height, width):
        for y in range(height):
            for x in range(width):
                point = Get(grid, x, y)
                #这里没有依赖关系
                Compare(grid, point, x, y, -1, 0)
                Compare(grid, point, x, y, 0, -1)
                Compare(grid, point, x, y, -1, -1)
                Compare(grid, point, x, y, 1, -1)
            for x in range(width - 1, -1, -1):
                point = Get(grid, x, y)
                Compare(grid, point, x, y, 1, 0)
                
        for y in range(height - 1, -1, -1):
            for x in range(width - 1, -1, -1):
                point = Get(grid, x, y)
                #这里没有依赖关系
                Compare(grid, point, x, y, 1, 0)
                Compare(grid, point, x, y, 0, 1)
                Compare(grid, point, x, y, -1, 1)
                Compare(grid, point, x, y, 1, 1)
            for x in range(width):
                point = Get(grid, x, y)
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
        
        ret = ComputeSDF(data, image.size[0], image.size[1])
        
        for y in range(image.size[1]):
            for x in range(image.size[0]):
                index = (y * image.size[0] + x) * 4
                val = ret[y * image.size[0] + x] / 255.0
                image.pixels[index] = val
                image.pixels[index + 1] = val
                image.pixels[index + 2] = val
                image.pixels[index + 3] = 1.0
        image.update()

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