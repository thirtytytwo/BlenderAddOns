from collections import defaultdict
import bpy
from mathutils import Vector
import math 

class ModifyMeshVertexOperator(bpy.types.Operator):
    bl_idname = "object.modifymeshvertex"
    bl_label = "ModifyMeshVertex"
        
    def execute(self, context):
        mesh = context.selected_objects[0].data
        verNomralDic = {}
        vertUVDic = defaultdict(lambda: defaultdict(list))
        vertNum = 0
        for loop in mesh.loops:
            vertIndex = loop.vertex_index
            normal = loop.normal
            normalConfirm = False
            uvConfirm = False
            # 检查法线
            if vertIndex not in verNomralDic:
                verNomralDic[vertIndex] = set()
                verNomralDic[vertIndex].add(Vector(normal).freeze())
                normalConfirm = True
            else:
                needsAdd = True
                for existing in verNomralDic[vertIndex]:
                    dot = (normal.x * existing[0] +normal.y * existing[1] +normal.z * existing[2])
                    dot = max(min(dot, 1.0), -1.0)
                    angle = math.degrees(math.acos(dot))
                    if angle < 4:
                        needsAdd = False
                        break
                if needsAdd:
                    verNomralDic[vertIndex].add(Vector(normal).freeze())
                    normalConfirm = True
            
            # 检查UV
            for uvLayer in mesh.uv_layers:
                if uvLayer.name == "OutlineUV":
                    continue
                data = uvLayer.data[loop.index].uv
                curUV = Vector((round(data.x, 3), round(data.y, 3)))
                curLayerName = uvLayer.name
                if not vertUVDic[vertIndex][curLayerName]:
                    uvConfirm = True
                else:
                    if any(uv.x != curUV.x or uv.y != curUV.y for uv in vertUVDic[vertIndex][curLayerName]):
                        uvConfirm = True
                        break
                vertUVDic[vertIndex][curLayerName].append(curUV)
            
            if normalConfirm or uvConfirm:
                vertNum += 1
                
        print("vertNum: ", vertNum)         
        return {"FINISHED"}

