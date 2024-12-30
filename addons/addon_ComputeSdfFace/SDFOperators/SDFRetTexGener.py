import concurrent.futures
import numpy as np
import bpy

class Point:
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy
    
    def GetDistance(self):
        return self.dx * self.dx + self.dy * self.dy
    
def ComputeSDF(image):
        width = image.size[0]
        height = image.size[1]
        res = max(width, height)
        
        grid1 = [[Point(0, 0) for x in range(width)] for y in range(height)]
        grid2 = [[Point(0, 0) for x in range(width)] for y in range(height)]
        
        for y in range(height):
            for x in range(width):
                if image.pixels[(y * width + x) * 4] < 0.5:
                    grid1[y][x] = Point(0, 0)
                    grid2[y][x] = Point(res, res)
                else:
                    grid1[y][x] = Point(res, res)
                    grid2[y][x] = Point(0, 0)
        #TODO 这里没有依赖关系，可以用两个线程做
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(ComputeGrid, grid1, height, width)
            future2 = executor.submit(ComputeGrid, grid2, height, width)
            future1.result()
            future2.result()

        #TODO 这里没有依赖关系，可以用多线程
        retImage = bpy.data.images.new(name = image.name + "_sdf", width = width, height = height)
        for y in range(height):
            for x in range(width):
                with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                    futures = []
                    for y in range(height):
                        for x in range(width):
                            futures.append(executor.submit(ComputePixel, grid1, grid2, retImage, x, y, width))
                    for future in futures:
                        future.result()
        retImage.update()

def ComputePixel(grid1, grid2, image, x, y, width):
    d1 = grid1[y][x].GetDistance()
    d2 = grid2[y][x].GetDistance()
    val = (d1 - d2) / (d1 + d2)
    normalized_value = (val + 1) / 2
    image.pixels[(y * width + x) * 4 : (y * width + x) * 4 + 4] = [normalized_value] * 4
        
def Get(grid, x, y):
    if x >= 0 and y >=0 and x < len(grid[0]) and y < len(grid):
        return grid[y][x]
    else:
        return Point(len(grid), len(grid))
        
def Compare(grid, point, x, y, offsetX, offsetY):
    otherP = Get(grid, x + offsetX, y + offsetY)
    otherP.dx += offsetX
    otherP.dy += offsetY
    
    if otherP.GetDistance() < point.GetDistance():
        point = otherP

def ComputeGrid(grid, height, width):
        for y in range(height):
            for x in range(width):
                point = Get(grid, x, y)
                #这里没有依赖关系
                Compare(grid, point, x, y, -1, 0)
                Compare(grid, point, x, y, 0, -1)
                Compare(grid, point, x, y, -1, -1)
                Compare(grid, point, x, y, 1, -1)
                grid[y][x] = point
            for x in range(width - 1, -1, -1):
                point = Get(grid, x, y)
                Compare(grid, point, x, y, 1, 0)
                grid[y][x] = point
                
        for y in range(height - 1, -1, -1):
            for x in range(width - 1, -1, -1):
                point = Get(grid, x, y)
                #这里没有依赖关系
                Compare(grid, point, x, y, 1, 0)
                Compare(grid, point, x, y, 0, 1)
                Compare(grid, point, x, y, -1, 1)
                Compare(grid, point, x, y, 1, 1)
                grid[y][x] = point
            for x in range(width):
                point = Get(grid, x, y)
                Compare(grid, point, x, y, -1, 0)
                grid[y][x] = point

class SDFRetTexGenOperator(bpy.types.Operator):
    bl_idname = "object.sdf_ret_gen"
    bl_label = "SDFRetTexGenOperator"
    
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.selected_objects[0].type == 'MESH'
    
    def execute(self, context):
        props = context.scene.SdfProperties
        
        images = []
        for tex in props.GeneratedTextures:
            images.append(tex.image)
        array = np.array(images[5].pixels[:], dtype=np.float32).reshape(images[5].size[1], images[5].size[0], 4)
        data = array[:, :, 0].flatten()
        
        #non_black_pixels = np.sum(data > 0)
        #non_black_pixels = np.sum(np.any(array[:, :, :3] > 0, axis=-1))
        #print(f"非黑色像素数量: {non_black_pixels}")
        with concurrent.futures.process.ProcessPoolExecutor(max_workers = len(images)) as executor:
            futures = []
            for image in images:
                array = np.array(image.pixels[:], dtype=np.float32).reshape(image.size[1], image.size[0], 4)
                data = array[:, :, 0].flatten()
                futures.append(executor.submit(ComputeSDF, data))
            
            for future in concurrent.futures.as_completed(futures):
                future.result()
        
        return {"FINISHED"}