#!/usr/bin/python
# -*- coding: latin-1 -*-



# =============================================================================================
# Librairies importation

import numpy as np
import nrrd
import sys
import os
import multiprocessing as mp
from voxcell import RegionMap
import voxcell


# =============================================================================================



# =============================================================================================
# Fonctions

def read_img(img_path = ""):
    """
    Reading a NPY or NRRD file
    @method read_img
    @param {String} img_path The path of the input image to be read (NPY or NRRD)
    @return {NumpyArray} A numpy array with values corresponding to the input image
    """

    ext = img_path.split(".")[-1]
    if ext == "nrrd":
        img, hd = nrrd.read(img_path)
    elif ext == "npy":
        img = np.load(img_path)
    else:
        print("ERROR: img_path " + ext + "file format not supported")
        return

    return img



def write_img(img_path = "", out_array_img = []):
    """
    Writing a NPY or NRRD file
    @method write_img
    @param {String} img_path The path of the image to be written (NPY or NRRD)
    @param {Array} out_array_img The array to be written at img_path
    @return {None} Writes the out_array_img at img_path
    """

    ext = img_path.split(".")[-1]
    if ext == "nrrd":
        nrrd.write(img_path, out_array_img)
    elif ext == "npy":
        np.save(img_path, out_array_img)
    else:
        print("ERROR: outuput file format not supported")
        return

    print("Image successfully written at path", img_path)

    return




def common_hierarchy_identification(input_annot_ccfv3_file_path = "", input_annot_ccfv2_file_path = "", hier_id = 0):
    """
    Identifying of the common non-empty hierarchy cetween CCFv2 and CCFv3
    @method common_hierarchy_identification
    @param {String} input_annot_ccfv3_file_path The path of the input CCFv3 annotation file
    @param {String} input_annot_ccfv2_file_path The path of the input CCFv2 annotation file
    @param {Integer} hier_id The ID of the hierarchy file
    @return {List} Returns the list of hier_id where there are voxel defined in both annotation volumes
    """

    # Reading the input file
    ccfv3_vol = read_img(input_annot_ccfv3_file_path)
    ccfv2_vol = read_img(input_annot_ccfv2_file_path)
    annot_vol_dim = ccfv3_vol.shape
    id_list = read_img(input_hier_id_file_list)

    # reading the hierarchy file
    hierarchy_input_path = "/gpfs/bbp.cscs.ch/project/proj62/piluso/data/00_allen_brain_atlas/1.json"
    region_map = RegionMap.load_json(hierarchy_input_path)

    # Setting all values to 0 except those in id_list that are set to 1
    print("Processing id_nb file", hier_id)

    # Evaluating if voxels are defined for a specific label
    ccfv3_has_value = np.any(ccfv3_vol == hier_id)
    ccfv2_has_value = np.any(ccfv2_vol == hier_id)
    if ccfv3_has_value and ccfv2_has_value:
        leaf = "yes"
        print("LEAF REGION")
    # Going through the parent ID if the region does not have any voxel defined
    else:
        leaf = "no"
        print("NOT LEAF REGION")
        while not (ccfv3_has_value and ccfv2_has_value):

            try:
                hier_id = region_map.get(hier_id, "parent_structure_id", with_ascendants=False)
                list_hier_ids = list(region_map.find(hier_id, "id", with_descendants=True))
                
            except voxcell.exceptions.VoxcellError:
                print("ERROR with region " + str(hier_id) + " which has not been found")
                return -1
            out = False
            i = 0
            while not out:
                try:
                    ccfv3_has_value = np.any(ccfv3_vol == list_hier_ids[i])
                    ccfv2_has_value = np.any(ccfv2_vol == list_hier_ids[i])
                    if ccfv3_has_value and ccfv2_has_value:
                        out = True
                    else:
                        i += 1
                except IndexError:
                    print("Skip: IndexError")
                    print("list_hier_ids", len(list_hier_ids))
                    out = True
                    pass

    print("final common hier number:", hier_id)

    return hier_id, leaf



def common_hierarchy_identification_multi(input_annot_ccfv3_file_path = "", input_annot_ccfv2_file_path = "", input_hier_id_file_list = "", output_folder= ""):
    """
    Identifying of the common non-empty hierarchy between CCFv2 and CCFv3 in a distributed mode
    @method common_hierarchy_identification_multi
    @param {String} input_annot_ccfv3_file_path The path of the input CCFv3 annotation file
    @param {String} input_annot_ccfv2_file_path The path of the input CCFv2 annotation file
    @param {String} input_hier_id_file_list The path of the input hierarchy id 
    @param {String} output_common_hier_list The path of the output common hierarchy list
    @param {String} output_folder The folder where to save data
    @return {None} Writes the common hier list
    """

    # Read the input image
    id_list = read_img(input_hier_id_file_list)

    # Distributed computing
    used_cpu = int(mp.cpu_count()/2)
    print("Starting parallel computing on " + str(used_cpu) + " nodes")
    pool = mp.Pool(used_cpu)
    output_list = []
    output_list.append(pool.starmap(common_hierarchy_identification, [(input_annot_ccfv3_file_path, input_annot_ccfv2_file_path, id_list[i]) for i in range(len(id_list))]))
    pool.close()

    # Sort and convert hier list into numpy array
    # Leaf regions
    leaf_list = [item[0] for item in output_list[0] if item[1] == "yes"]
    print("\nleaf_list_raw", leaf_list)
    leaf_list = sorted(leaf_list)
    leaf_list = np.array(leaf_list)
    leaf_list = np.unique(leaf_list)
    leaf_list = leaf_list[leaf_list >= 0]
    print("\nleaf_list", leaf_list)

    # Non leaf regions
    non_leaf_list = [item[0] for item in output_list[0] if item[1] == "no"]
    print("\nnon_leaf_list_raw", non_leaf_list)
    non_leaf_list = sorted(non_leaf_list)
    non_leaf_list = np.array(non_leaf_list)
    non_leaf_list = np.unique(non_leaf_list)
    non_leaf_list = non_leaf_list[non_leaf_list >= 0]
    print("\nnon_leaf_list", non_leaf_list)

    # Writing the output result
    output_leaf_path = os.path.join(output_folder, "grey_common_hier_leaf.npy")
    output_nonleaf_path = os.path.join(output_folder, "grey_common_hier_nonleaf.npy")
    write_img(output_leaf_path, leaf_list)
    write_img(output_nonleaf_path, non_leaf_list)

    return


# =============================================================================================





# =============================================================================================
# Executions

# Command to system
input_annot_ccfv3_file_path = os.path.abspath(sys.argv[1])
input_annot_ccfv2_file_path = os.path.abspath(sys.argv[2])
input_hier_id_file_list = os.path.abspath(sys.argv[3])
output_folder = os.path.abspath(sys.argv[4])


print("Starting common_hierarchy_identification_multi...")
print("input_annot_ccfv3_file_path:", input_annot_ccfv3_file_path)
print("input_annot_ccfv2_file_path:", input_annot_ccfv2_file_path)
print("input_hier_id_file_list:", input_hier_id_file_list)
print("output_folder:", output_folder)

print("Processing...")
common_hierarchy_identification_multi(input_annot_ccfv3_file_path, input_annot_ccfv2_file_path, input_hier_id_file_list, output_folder)
print("Done: common hierarchy successfully identified")
# =============================================================================================
