#!/usr/bin/python
# -*- coding: latin-1 -*-



# =============================================================================================
# Librairies importation

import numpy as np
import nrrd
import sys
import os
from voxcell import RegionMap

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




def get_boolean_input(value_to_convert = ""):
        if value_to_convert in ["yes", "y"]:
            return True
        elif value_to_convert in ["no", "n"]:
            return False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")
            return



def hierarchy_ids(output_folder = "", region_name = "", with_descendants = "", leaf_region = "", write_result = "yes", leaves_only = ""):
    """
    Identifying the ID hierarchy 
    @method hierarchy_ids
    @param {String} output_folder The path of the output folder where to save all the corresponding IDs
    @param {String} region_name The name of the region of interest
    @param {String} leaf_region If we only want leaf regions
    @param {String} write_result To write or not the result
    @param {String} leaves_only leaf to load the leaves_only hierarchy file, nothing else
    @return {None} Writes all IDs from the hierarchy file included in region_name
    """

    # Reading the input file
    if leaves_only == "leaf":
        print("leaves_only hierarchy")
        hierarchy_input_path = "/gpfs/bbp.cscs.ch/home/piluso/cell_atlas/05_final_run/blue_brain_atlas_pipeline/leaves_only/hierarchy_ccfv2_l23split_barrelsplit.json"
    else:
        hierarchy_input_path = "/home/piluso/data/00_allen_brain_atlas/1.json"
    region_map = RegionMap.load_json(hierarchy_input_path)

    # Identifying the id correponding at the region of interest
    region_acronym = region_map.get(region_map.find(region_name, "name").pop(), "acronym")
    ids = region_map.find(region_acronym, "acronym", with_descendants=get_boolean_input(with_descendants))
    ids_array = np.fromiter(ids, int, len(ids))

    if leaf_region == "yes":
        print("Leaf regions only")
        ids_array = [id_val for id_val in ids_array if region_map.is_leaf_id(id_val) ]

    else:
        pass

    print("acronym:", region_acronym)
    print("ids:", ids_array)
    print("number of ids:", len(ids_array))

    # Writing the output result
    if write_result == "yes":
        output_path = os.path.join(output_folder, region_acronym + ".npy")
        write_img(output_path, ids_array)
    else:
        pass

    return


# =============================================================================================





# =============================================================================================
# Executions

# Command to system
output_folder = os.path.abspath(sys.argv[1])
region_name = sys.argv[2]
with_descendants = sys.argv[3]
leaf_region = sys.argv[4]
write_result = sys.argv[5]
leaves_only = sys.argv[6]

region_name = region_name.replace("_", " ")
region_name = region_name.replace("---", "(")
region_name = region_name.replace("--", ")")
region_name = region_name.replace("+", "\'")

print("Starting hierarchy_ids...")
print("output_folder:", output_folder)
print("region_name:", region_name)
print("with_descendants:", with_descendants)
print("leaf_region:", leaf_region)
print("write_result:", write_result)
print("leaves_only", leaves_only)

print("Processing...")
hierarchy_ids(output_folder, region_name, with_descendants, leaf_region, write_result, leaves_only)
print("Done: ID successfully identified from hierarchy")
# =============================================================================================
