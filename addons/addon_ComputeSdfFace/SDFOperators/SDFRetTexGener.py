import bpy
from concurrent.futures import ThreadPoolExecutor

class Point:
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy
    
    def GetDistance(self):
        return self.dx * self.dx + self.dy * self.dy

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
        
        retImages = []
        #executor = ThreadPoolExecutor(max_workers=len(images))
        #for result in executor.map(self.ComputeSDF, images):
            #retImages.append(result)
        
        self.ComputeSDF(images[0])
        
        return {"FINISHED"}

    def ComputeSDF(self, image):
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
        # with ThreadPoolExecutor(max_workers=2) as executor:
        #     future1 = executor.submit(self.ComputeGrid, grid1, height, width)
        #     future2 = executor.submit(self.ComputeGrid, grid2, height, width)
        #     future1.result()
        #     future2.result()
        
        #TODO 这里没有依赖关系，可以用多线程
        for y in range(height):
            for x in range(width):
                # d1 = grid1[y][x].GetDistance()
                # d2 = grid2[y][x].GetDistance()
                # val = (d1 - d2) / (d1 + d2)
                # normalized_value = (val + 1) / 2
                
                image.pixels[(y * width + x) * 4 : (y * width + x) * 4 + 4] = [1, 1, 1, 1]
        image.update()

    def Get(self, grid, x, y):
        if x >= 0 and y >=0 and x < len(grid[0]) and y < len(grid):
            return grid[y][x]
        else:
            return Point(len(grid), len(grid))
    def Compare(self, grid, point, x, y, offsetX, offsetY):
        otherP = self.Get(grid, x + offsetX, y + offsetY)
        otherP.dx += offsetX
        otherP.dy += offsetY
        
        if otherP.GetDistance() < point.GetDistance():
            point = otherP

    def ComputeGrid(self, grid, height, width):
            for y in range(height):
                for x in range(width):
                    point = self.Get(grid, x, y)
                    #这里没有依赖关系
                    self.Compare(grid, point, x, y, -1, 0)
                    self.Compare(grid, point, x, y, 0, -1)
                    self.Compare(grid, point, x, y, -1, -1)
                    self.Compare(grid, point, x, y, 1, -1)
                    grid[y][x] = point
                for x in range(width - 1, -1, -1):
                    point = self.Get(grid, x, y)
                    self.Compare(grid, point, x, y, 1, 0)
                    grid[y][x] = point
                    
            for y in range(height - 1, -1, -1):
                for x in range(width - 1, -1, -1):
                    point = self.Get(grid, x, y)
                    #这里没有依赖关系
                    self.Compare(grid, point, x, y, 1, 0)
                    self.Compare(grid, point, x, y, 0, 1)
                    self.Compare(grid, point, x, y, -1, 1)
                    self.Compare(grid, point, x, y, 1, 1)
                    grid[y][x] = point
                for x in range(width):
                    point = self.Get(grid, x, y)
                    self.Compare(grid, point, x, y, -1, 0)
                    grid[y][x] = point