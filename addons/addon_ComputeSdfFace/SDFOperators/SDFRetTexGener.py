import bpy
import math
from concurrent.futures import ThreadPoolExecutor

class SDFRetTexGenOperator(bpy.types.Operator):
    bl_idname = "object.sdf_ret_gen"
    bl_label = "SDFRetTexGenOperator"
    
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.selected_objects[0].type == 'MESH'
    
    def execute(self, context):
        props = context.scene.SdfProperties
        images = None
        
        for i in len(props.GeneratedTextures):
            images.append(props.GeneratedTextures[i].image)
        
        with ThreadPoolExecutor() as executor:
            executor.map(self.GenerateRetTex, images)
    
    def GetGrid(self, grid, x, y):
        return grid[y][x]
    
    def Compare(self, grid, point, x, y, offsetX, offsetY):
        otherP = self.GetGrid(grid, x + offsetX, y + offsetY)
        otherP.dx += offsetX
        otherP.dy += offsetY
        
        if otherP.dist < point.dist:
            point = otherP

    def ComputeSDF(self, grid, height, width):
            for y in range(height):
                for x in range(width):
                    point = self.GetGrid(grid, x, y)
                    self.Compare(grid, point, x, y, -1, 0)
                    self.Compare(grid, point, x, y, 0, -1)
                    self.Compare(grid, point, x, y, -1, -1)
                    self.Compare(grid, point, x, y, 1, -1)
                for x in range(width - 1, -1, -1):
                    point = self.GetGrid(grid, x, y)
                    self.Compare(grid, point, x, y, 1, 0)
            
            for y in range(height - 1, -1, -1):
                for x in range(width - 1, -1, -1):
                    point = self.GetGrid(grid, x, y)
                    self.Compare(grid, point, x, y, 1, 0)
                    self.Compare(grid, point, x, y, 0, 1)
                    self.Compare(grid, point, x, y, -1, 1)
                    self.Compare(grid, point, x, y, 1, 1)
                for x in range(width):
                    point = self.GetGrid(grid, x, y)
                    self.Compare(grid, point, x, y, -1, 0)