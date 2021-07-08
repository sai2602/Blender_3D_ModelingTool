import bpy

#light settings
light = bpy.data.objects['Light']
light.select_set(True)
light.location[0] = 0
light.location[1] = 0
light.location[2] = 21
light.data.energy = 2200
bpy.ops.object.select_all(action='DESELECT')

#camera settings
camera = bpy.data.objects['Camera']
camera.select_set(True)
camera.location[0] = 0
camera.location[1] = 0
camera.location[2] = 60
camera.rotation_euler[0] = 0
camera.rotation_euler[1] = 0
camera.rotation_euler[2] = 0

scene = bpy.context.scene
dir_name = 'C:/Blender/Images/Material'

scene.render.engine = 'CYCLES'
scene.view_layers["View Layer"].use_pass_object_index = True
scene.render.image_settings.color_depth = '16'
bpy.context.scene.cycles.samples = 16

#compositing for Depth map
def DepthMap(scene):
    
    scene.use_nodes = True
    tree = scene.node_tree
    nodes = tree.nodes
    links = tree.links
    
    for node in nodes:
        if(not(node.name.startswith('Render Layers') or node.name.startswith('Composite'))):
           nodes.remove(node)
    
    mapvalue = tree.nodes.new(type = "CompositorNodeMapValue")
    mapvalue.offset[0] = -60
    mapvalue.size[0] = 0.08

    for link in links:
        links.remove(link)

    depth = tree.nodes['Render Layers'].outputs[2]
    to_value = mapvalue.inputs[0]
    from_value = mapvalue.outputs[0]
    img = tree.nodes['Composite'].inputs[0]

    links.new(depth,to_value)
    links.new(from_value,img)

# Get material
mat = bpy.data.materials.get("Material")

if mat is None:
    # create material
    mat = bpy.data.materials.new(name="Material")

nodes = mat.node_tree.nodes

for eachnode in nodes:
    if(eachnode.name == 'Principled BSDF'):
        principled_bsdf_node = eachnode
        
principled_bsdf_node.inputs['Metallic'].default_value = 0.5
principled_bsdf_node.inputs['Specular'].default_value = 0.5
principled_bsdf_node.inputs['Roughness'].default_value = 0.2
principled_bsdf_node.inputs['Sheen Tint'].default_value = 0.5
principled_bsdf_node.inputs['Alpha'].default_value = 0.5
mat.blend_method = 'BLEND'

for object in bpy.data.objects:
    if(object.name.startswith('Cloth')):
        if(object.data.materials):
            object.data.materials[0] = mat
        else:
            object.data.materials.append(mat)
    else:
        if(not(object.name.startswith('Camera') or object.name.startswith('Light'))):
            object.data.materials.clear()

depth_dir_name = dir_name + '/DepthMap'
DepthMap(scene)
scene.render.filepath = depth_dir_name + '/Render'
bpy.ops.render.render(write_still=True)
