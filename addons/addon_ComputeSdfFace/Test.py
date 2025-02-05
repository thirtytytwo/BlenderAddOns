import math
import time
import numpy as np
import bpy

def ComputeSDF(data,size):
    
    grid1 = [[(0,0,0) for _ in range(size + 2)] for _ in range(size + 2)]
    grid2 = [[(0,0,0) for _ in range(size + 2)] for _ in range(size + 2)]
    
    for y in range(-1, size + 1):
        for x in range(-1, size + 1):
            if x < 0 or y < 0 or x >= size or y >= size:
                grid1[y + 1][x + 1] = (size, size, size * size)
                grid2[y + 1][x + 1] = (size, size, size * size)
                continue
            elif data[(y * size + x)] < 0.5:
                grid1[y + 1][x + 1] = (0, 0, 0)
                grid2[y + 1][x + 1] = (size, size, size * size)
            else:
                grid1[y + 1][x + 1] = (size, size, size * size)
                grid2[y + 1][x + 1] = (0, 0, 0)
    
    ComputeGrid(grid1,size)
    ComputeGrid(grid2,size)
    
    result = []
    for i in range(size):
        for j in range(size):
            dist = math.sqrt(float(grid1[i + 1][j + 1][2])) - math.sqrt(float(grid2[i + 1][j + 1][2]))
            val = dist * 3 + 128
            if val < 0: val = 0
            if val > 255: val = 255
            result.append(val / 255.0)
    return result

def ComputeGrid(grid, size):
    offsetBottomLeft = [-1, 0, -1, 1, 0, -1, -1, -1]
    offsetTopRight = [1, 0, -1, 1, 0, 1, 1, 1]
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
            p1 = grid[y][x-1]
            xVal = p1[0] - 1
            yVal = p1[1]
            dist = xVal * xVal + yVal * yVal
            if dist < p0[2]:
                grid[y][x] = (xVal, yVal,dist)





startTime = time.time()
image = bpy.data.images.get('SDFTexture1')
if image is None:
    raise ValueError("Image 'SDFTexture1' not found in the scene")

size = int(image.size[0])

data = np.array(image.pixels[:], dtype=np.float32).reshape(size, size, 4)
data = data[:, :, 0].flatten()

resultData = ComputeSDF(data, size)
elapsedTime = time.time() - startTime
print(f"逻辑运行时间: {elapsedTime:.2f} 秒")

startTime = time.time()
pixelData = np.zeros(size * size * 4, 'f')
pixelData[0::4] = resultData[:]
pixelData[1::4] = resultData[:]
pixelData[2::4] = resultData[:]
pixelData[3::4] = 1.0
image.pixels.foreach_set(pixelData.ravel())
image.update()

elapsedTime = time.time() - startTime
print(f"应用结果数据时间: {elapsedTime:.2f} 秒")
        