import bpy
import bmesh

class ModifyMeshVertexOperator(bpy.types.Operator):
    bl_idname = "object.modifymeshvertex"
    bl_label = "ModifyMeshVertex"

    def split_sharp_edge(self, bm, edge):
        # 检查每个顶点的相连边是否有其他锐边
        for vert in edge.verts:
            sharpEdges = [e for e in vert.link_edges if not e.smooth and e != edge]
            for sharpEdge in sharpEdges:
                # 找到相连的面并删除
                for face in vert.link_faces:
                    if edge in face.edges and sharpEdge in face.edges:
                        # 新的顶点
                        result = bmesh.ops.split(bm, geom=[vert])
                        newVert = result['geom'][0]
                        newVert.co = vert.co
                        newVert.normal = face.normal
                        # 另外n个顶点
                        verts = []
                        for v in face.verts:
                            if v == vert:
                                verts.append(newVert)
                            else:
                                verts.append(v)
                        if len(verts) > 4:
                            self.report({'ERROR'}, "Face has more than 4 vertices")
                            return {'CANCELLED'}
                        # 组织新的面，由另外n个顶点和新的顶点组成
                        newFace = bm.faces.new(verts)
                        newFace.smooth = face.smooth    
                        # 将新的面的边标记为平滑边
                        for e in newFace.edges:
                            e.smooth = True
                        # 删除面
                        bm.faces.remove(face)
                        bm.faces.index_update()
        # 将当前锐边标记为非锐边
        edge.smooth = True

        
    def execute(self, context):
        mesh = context.object.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        
        for edge in bm.edges:
            if not edge.smooth:
                print(f"Edge{edge.index}is sharp.")
                self.split_sharp_edge(bm, edge)
        
        bm.to_mesh(mesh)
        mesh.update()   
        bm.free()
        return {"FINISHED"}

