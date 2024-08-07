import bpy
import bmesh

def count_unique_uvs(mesh, uv_layer_name="UVSet0", uv_layer_name1 = "UVSet1"):
    # Ensure the mesh has a UV map
    if uv_layer_name not in mesh.uv_layers:
        print(f"UV layer '{uv_layer_name}' not found.")
        return 0
    
    uv_layer = mesh.uv_layers[uv_layer_name].data
    
    # Create a BMesh from the mesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    # Ensure the UV layer exists in the BMesh
    uv_layer_bm = bm.loops.layers.uv.get(uv_layer_name)
    if not uv_layer_bm:
        print(f"UV layer '{uv_layer_name}' not found in BMesh.")
        return 0
    
    # Set to store unique UV coordinates
    unique_uvs = set()
    
    # Traverse all faces and loops
    for face in bm.faces:
        for loop in face.loops:
            uv = loop[uv_layer_bm].uv
            uv_key = (loop.vert.co.x,loop.vert.co.y,loop.vert.co.z,uv.x, uv.y)  # Use rounded UV coordinates as key
            unique_uvs.add(uv_key)
    
    # Write the BMesh back to the mesh
    bm.to_mesh(mesh)
    bm.free()
    
    return len(unique_uvs)

# Example usage
obj = bpy.context.active_object
if obj and obj.type == 'MESH':
    unique_uv_count = count_unique_uvs(obj.data)
    print(f"Number of unique UVs: {unique_uv_count}")