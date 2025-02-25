import bpy
import bmesh

class ModifyMeshVertexOperator(bpy.types.Operator):
    bl_idname = "object.modifymeshvertex"
    bl_label = "ModifyMeshVertex"

    # def split_sharp_edge(self, bm, face, edges):
    #     # 新增的顶点容器
    #     newVerts = []
    #     # 根据两两相交锐边的相交点去增加顶点
    #     for edge in edges:
    #         for vert in edge.verts:
    #             for e in vert.link_edges:
    #                 if e in edges and e != edge:
    #                     if vert.co not in [v.co for v in newVerts]:
    #                         v = bm.verts.new(vert.co, vert)
    #                         v.normal = face.normal
    #                         newVerts.append(v)
        
    #     # 修改面
    #     if newVerts is not None:
    #         faceVerts = []
    #         for vert in face.verts:
    #             flag = False
    #             for v in newVerts:
    #                 if vert.co == v.co:
    #                     flag = True
    #                     faceVerts.append(v)
    #                     break
    #             if not flag:
    #                 faceVerts.append(vert)
    #         newFace = bm.faces.new(faceVerts)
    #         newFace.smooth = face.smooth
    #         newFace.material_index = face.material_index
    #         bm.faces.remove(face)
        
    def execute(self, context):
        mesh = context.object.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        
        
        
        bm.to_mesh(mesh)
        mesh.update()   
        bm.free()
        return {"FINISHED"}

