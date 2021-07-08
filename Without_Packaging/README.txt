1. Import the .stl bin which is to be used and scale it to the standard size (dimensions provided in the sample bin in 'bins' folder)
2. add a plane (mesh) with the X and Y dimensions matching that of the bin
3. Place this plane at the bottom of the bin (just touching the bottom of the bin but also visible from top view)
4. Rename the bin such that it starts with the term 'Bin' (case sensitive) and also the plane starts with 'CollisionPlane' (case sensitive)
5. export the bin and the plane as .obj file
6. specify the location of bin (.obj file), the object (.stl file) and the location where the images are to be saved in the variables 'bin_loc_base', 'obj_loc_base' and 'img_loc_base' respectively
7. change the number of objects to be added with the variable 'num_of_objs'
8. Copy the code in the scripting tab of the scene and run script
9. If the depth maps are not per expectation, its better to play around with the MapValue offset (mapvalue.offset[0] = -55 in the DepthMap sub function) to see which number suits the best.