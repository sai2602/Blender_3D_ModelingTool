#Latest Code
##################################################################################
## Important Note:                                                              ##
## At times, the blender simulation causes the mesh to push through the plane.  ##
## This leads to the object falling through the bin                             ##
## When this occurs, create a new blender scene / close and re-open blender     ##
## Re-run the script now and the simulations will work fine                     ##
##################################################################################

#####################################
#Change was adding the lines:       #
#    for obj in bpy.data.objects:   #
#        obj.hide_render = False    #
#                                   #
#Reason was that the parts were     #
#not visible in segmentation mask   #
#and RGB render as the hide port    #
#was always true. This fixed the    #
#issue                              #
#####################################

import bpy
import random
import csv
from os import listdir, mkdir, rename
from shutil import rmtree
from os.path import isfile, join, exists, dirname, abspath
from math import degrees
from PIL import Image

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

#scene objects and rendered info locations
bin_loc_base = 'C:/muk/Blender_Simulation/With_Packaging/Bins'
obj_loc_base = 'C:/muk/CAD_Models/Workpieces/Sosta'
img_loc_base = 'C:/Test/Run'
num_of_objs = 2
Header = ['X','Y','Z','ID']
Pose_Header = ['X','Y','Z','Rot_X','Rot_Y','Rot_Z','ID']

#extracting all the available wrapped bins info (all bins to be placed in the same directory)
bins = [b for b in listdir(bin_loc_base) if isfile(join(bin_loc_base, b))]
parts = [p for p in listdir(obj_loc_base) if isfile(join(obj_loc_base, p))]

#directory labels
cyclenumber = 0 #signifies cycle number

#setting up the scene
scene = bpy.context.scene
scene.frame_start = 1 
scene.frame_end = 250
scene.render.engine = 'CYCLES'
scene.view_layers["View Layer"].use_pass_object_index = True
scene.render.image_settings.color_depth = '16'
bpy.context.scene.cycles.samples = 16

part_name = ''
pass_index_value = 1

def scenario(bin_loc, obj_loc, img_loc, Header, scene, num_of_objs, cyclenumber):
 
    global pass_index_value
    
    #deleting all the existing objects from the scene (except light and camera)
    bpy.ops.object.select_all(action='SELECT')
    bpy.data.objects['Camera'].select_set(False)
    bpy.data.objects['Light'].select_set(False)
    bpy.ops.object.delete()
    
    #deleting any hidden mesh objects
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block) 
            
    bpy.ops.ptcache.free_bake_all()
    
    #IDs for the objects in the scene (used for point cloud)
    BinID = 10
    WrappingID = 15
    ObjID = 20
    
    #import the bin
    imported_bin = bpy.ops.import_scene.obj(filepath=bin_loc)
    bpy.ops.object.select_all(action='DESELECT')
    
    #modifiers for the collision plane (at the bottom of the bin)
    collision_objs = [obj for obj in scene.objects if obj.name.startswith("Collision")]
    collision_objs[0].select_set(True)
    bpy.context.view_layer.objects.active = collision_objs[0]
    bpy.ops.rigidbody.objects_add(type = 'PASSIVE')
    bpy.ops.rigidbody.shape_change(type='MESH')
    bpy.ops.object.modifier_add(type = "COLLISION")
    collision_objs[0].modifiers.new(name = "planesolidify", type = "SOLIDIFY").thickness = 0.03
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    collision_objs[0].pass_index = pass_index_value
    collision_objs[0].select_set(False)
    
    #modifiers for the bin
    bin_objs = [obj for obj in scene.objects if obj.name.startswith("Bin")]
    bin_objs[0].select_set(True)
    bpy.context.view_layer.objects.active = bin_objs[0]
    bpy.ops.object.modifier_add(type = "COLLISION")
    bpy.ops.rigidbody.objects_add(type = 'PASSIVE')
    bpy.ops.rigidbody.shape_change(type='MESH')
    bin_objs[0].modifiers.new(name = "binsolidify", type = "SOLIDIFY").thickness = 0.01
    bin_objs[0].pass_index = pass_index_value
    bin_objs[0].select_set(False)
    
    pass_index_value += 1

    #modifiers for the packaging (in this case, the cloth)
    for clothobj in bpy.data.objects:
        if(clothobj.name.startswith('Cloth')):
            clothobj.select_set(True)
            bpy.ops.rigidbody.objects_add(type = 'PASSIVE')
            clothobj.rigid_body.type = 'PASSIVE'
            bpy.ops.rigidbody.shape_change(type='MESH')
            clothobj.rigid_body.restitution = 0.5
            clothobj.pass_index = pass_index_value
            clothobj.select_set(False)
   
    scene.frame_current = 250
    pass_index_value += 1

    #import the object (which is dropped into the bin) and add the modifiers
    bpy.ops.import_mesh.stl(filepath = obj_loc)
    bpy.context.object.scale[0] = 0.03
    bpy.context.object.scale[1] = 0.03
    bpy.context.object.scale[2] = 0.03
    bpy.ops.rigidbody.object_add()
    bpy.ops.object.modifier_add(type = "COLLISION")
    bpy.context.object.rigid_body.type = 'ACTIVE'
    bpy.ops.rigidbody.shape_change(type='MESH')
    bpy.context.object.rigid_body.mass = 0.5
    bpy.context.object.rigid_body.restitution = 0.5
    bpy.context.object.location[0] = 0
    bpy.context.object.location[1] = 0
    bpy.context.object.location[2] = 0
    bpy.context.object.pass_index = pass_index_value
    pass_index_value += 1
    bpy.ops.object.select_all(action='DESELECT')

    for obj_cnt in range(num_of_objs - 1):
        bpy.ops.import_mesh.stl(filepath = obj_loc)
        bpy.context.object.scale[0] = 0.03
        bpy.context.object.scale[1] = 0.03
        bpy.context.object.scale[2] = 0.03
        bpy.ops.rigidbody.object_add()
        bpy.ops.object.modifier_add(type = "COLLISION")
        bpy.context.object.rigid_body.type = 'ACTIVE'
        bpy.context.object.rigid_body.mass = 0.5
        bpy.context.object.rigid_body.restitution = 0.5
        bpy.context.object.location[0] = random.uniform(-5,5)
        bpy.context.object.location[1] = random.uniform(-2.75,2.75)
        bpy.context.object.location[2] = 3 + (0.25*obj_cnt)
        bpy.context.object.rotation_euler[2] = random.randrange(-90, 90)
        bpy.context.object.rigid_body.kinematic = True
        bpy.context.object.keyframe_insert(data_path="rigid_body.kinematic",frame = 0)
        bpy.context.object.rigid_body.kinematic = False
        bpy.context.object.keyframe_insert(data_path="rigid_body.kinematic",frame = 10 + (obj_cnt*10))
        bpy.context.object.pass_index = pass_index_value
        pass_index_value += 1
        bpy.ops.object.select_all(action='DESELECT')
    
    #bake all the physics and goto the end of the frame to render the image
    bpy.ops.ptcache.bake_all(bake=True)
    scene.frame_current = 250

    bpy.ops.ptcache.free_bake_all()
    
    pass_index_value -= 1 #pass index will become one more than the number of objects because of the exit loop increment
    
    #creating directories to store info pertaining to each cycle    
    dir_name = img_loc + '/Bin_' + str(cyclenumber)
    if not exists(dir_name):
        mkdir(dir_name)
    else:
        rmtree(dir_name)
        print('Deleted the existing directory ' + 'Bin_' + str(cyclenumber))
        print('Creating new empty directory')
        mkdir(dir_name)

    for obj in bpy.data.objects:
            obj.hide_render = False

    #rendered image for depth map
    depth_dir_name = dir_name + '/DepthMaps'
    DepthMap(scene)
    scene.render.filepath = depth_dir_name + '/DepthMap_ID' + str(pass_index_value)
    bpy.ops.render.render(write_still=True)
    
    for ID in range(1,pass_index_value):
            SubMasks(ID, depth_dir_name,'/DepthMap_ID')

    for obj in bpy.data.objects:
        obj.hide_render = False                
    
    #rendered image for segmentation mask
    segment_dir_name = dir_name + '/SegmentationMasks'
    SegmentationMask(scene)
    scene.render.filepath = segment_dir_name +'/SegmentationMask_ID' + str(pass_index_value)
    bpy.ops.render.render(write_still=True)
    
    for ID in range(1,pass_index_value):
            SubMasks(ID, segment_dir_name,'/SegmentationMask_ID')

    for obj in bpy.data.objects:
        obj.hide_render = False            
            
    #rendered image for RGB mask
    RGB_dir_name = dir_name + '/RGBMasks'
    AddTextures()
    RGBRender(scene)
    scene.render.filepath = RGB_dir_name +'/RGBMask_ID' + str(pass_index_value)
    bpy.ops.render.render(write_still=True)
    
    for ID in range(1,pass_index_value):
            SubMasks(ID, RGB_dir_name,'/RGBMask_ID')    


#Add textures to various objects
def AddTextures():
    cloth_mat = bpy.data.materials.new(name="Cloth_Material")

    cloth_mat.use_nodes = True
    nodes = cloth_mat.node_tree.nodes

    for eachnode in nodes:
        if(eachnode.name == 'Principled BSDF'):
            principled_bsdf_node = eachnode
            
    principled_bsdf_node.inputs['Metallic'].default_value = 0.5
    principled_bsdf_node.inputs['Specular'].default_value = 0.5
    principled_bsdf_node.inputs['Roughness'].default_value = 0.2
    principled_bsdf_node.inputs['Sheen Tint'].default_value = 0.5
    principled_bsdf_node.inputs['Alpha'].default_value = 0.5
    cloth_mat.blend_method = 'BLEND'
    
    bin_mat = bpy.data.materials.new("Bin_Material")
    bin_mat.diffuse_color = (0.0,0.0,1.0,1.0)
    
    for object in bpy.data.objects:
        if(object.name.startswith('Cloth')):
            if(object.data.materials):
                object.data.materials[0] = cloth_mat
            else:
                object.data.materials.append(cloth_mat)
                
        elif(object.name.startswith('Bin') or object.name.startswith('CollisionPlane')):
            object.active_material = bin_mat
            
        elif(not(object.name.startswith('Camera') or object.name.startswith('Light'))):
            object.data.materials.clear()
            
        else:
            pass
            
    

#un-hide the object with the pass_index(ID) and render the scene
def SubMasks(ID, dir_name, img_prefix):
    global part_name
    if(ID == 1):
        for obj in bpy.data.objects:
            if(obj.name.startswith(part_name) or obj.name.startswith('Cloth')):
                obj.hide_render = True
            else:
                obj.hide_render = False
    
    elif(ID == 2):
        for obj in bpy.data.objects:
            if(obj.name.startswith(part_name)):
                obj.hide_render = True
            else:
                obj.hide_render = False
        
    else:
        for obj in bpy.data.objects:
            if(obj.name.startswith(part_name) and (obj.pass_index > ID)):
                obj.hide_render = True
            else:
                obj.hide_render = False     
    
                
    scene.render.filepath = dir_name + img_prefix + str(ID)
    bpy.ops.render.render(write_still=True)



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
    mapvalue.offset[0] = -61
    mapvalue.size[0] = 0.08

    for link in links:
        links.remove(link)

    depth = tree.nodes['Render Layers'].outputs[2]
    to_value = mapvalue.inputs[0]
    from_value = mapvalue.outputs[0]
    img = tree.nodes['Composite'].inputs[0]

    links.new(depth,to_value)
    links.new(from_value,img)

#compositing for ID mask    
def SegmentationMask(scene):
    
    global pass_index_value
    
    scene.use_nodes = True
    nodes = scene.node_tree.nodes
    links = scene.node_tree.links
    for node in nodes:
        if(not(node.name.startswith('Render Layers'))):
            nodes.remove(node)
        else:
            render_layer_node = node

    number_of_idmasks = pass_index_value - 1

    for id in range(number_of_idmasks):
        ID = id + 1
        mask_node = nodes.new(type='CompositorNodeIDMask')
        mask_node.index = ID
        link = links.new(render_layer_node.outputs['IndexOB'], mask_node.inputs[0])
        
        multiply_node = nodes.new(type='CompositorNodeMath')
        multiply_node.operation = 'MULTIPLY'
        multiply_node.use_clamp = False
        link = links.new(render_layer_node.outputs['IndexOB'], multiply_node.inputs[0])
        link = links.new(mask_node.outputs[0], multiply_node.inputs[1])
        
        if id == 0:
            last_add = multiply_node
        else:
            add_node = nodes.new(type='CompositorNodeMath')
            add_node.operation = 'ADD'
            add_node.use_clamp = False
            link = links.new(last_add.outputs[0], add_node.inputs[0])
            link = links.new(multiply_node.outputs[0], add_node.inputs[1])
            last_add = add_node
    
    divide_node = nodes.new(type='CompositorNodeMath')
    divide_node.operation = 'DIVIDE'
    divide_node.use_clamp = False
    link = links.new(last_add.outputs[0], divide_node.inputs[0])
    divide_node.inputs[1].default_value = 256.0    

    comp_node = nodes.new(type= 'CompositorNodeComposite')
    links.new(divide_node.outputs[0], comp_node.inputs[0])
    
 
#compositing for RGB Image
def RGBRender(scene):
    
    scene.use_nodes = True
    tree = scene.node_tree
    nodes = tree.nodes
    links = tree.links
    
    for node in nodes:
        if(not(node.name.startswith('Render Layers') or node.name.startswith('Composite'))):
           nodes.remove(node)
    

    for link in links:
        links.remove(link)

    RGB_Img = tree.nodes['Render Layers'].outputs[0]
    Render_Capture = tree.nodes['Composite'].inputs[0]

    links.new(RGB_Img,Render_Capture)
 

###Start of main function
for part_index in range(len(parts)):
    part_name = parts[part_index].split('_')[0]
    obj_loc = join(obj_loc_base,parts[part_index])
    img_loc = img_loc_base + '/Part_' + part_name
    cyclenumber = 0   

    if not exists(img_loc):
        mkdir(img_loc)
    else:
        rmtree(img_loc)
        print('Deleted the existing directory ' + img_loc)
        print('Creating new empty directory')
        mkdir(img_loc)
  
    #simulation for each bin
    for bin_index in range(len(bins)):    
        bin_loc = join(bin_loc_base,bins[bin_index])
        scenario(bin_loc, obj_loc, img_loc, Header, scene, num_of_objs, cyclenumber)
        cyclenumber += 1
        pass_index_value = 1