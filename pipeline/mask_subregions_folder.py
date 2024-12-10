#!/usr/bin/python
# -*- coding: latin-1 -*-



# =============================================================================================
# Librairies importation

import numpy as np
import nrrd
import sys
import os
import multiprocessing as mp

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




def mask_sub_regions(input_data_path = "", input_mask_path = "", output_path = ""):
    """
    Masking sub-region labels
    @method mask_sub_regions
    @param {String} input_data_path The input path for the data regions to be masked
    @param {String} input_mask_path The input path where to the mask corresponding sub-region
    @param {String} output_path The output path where to write all the masked file
    @return {None} Writes the masked file at output_path
    """

    # Checking if output path exists
    # if os.path.exists(output_path):
    #     print("Skip: file " + os.path.basename(output_path) + " already exists")
    # else:

    # Checking if filenames are the same
    data_name = os.path.basename(input_data_path).split("_")[0]
    mask_name = os.path.basename(input_mask_path).split("_")[0]

    if data_name == mask_name:
        # Reading the input image
        input_data = read_img(input_data_path)
        input_mask = read_img(input_mask_path)

        # Masking using a multiplication with the mask file
        masked_data = input_data*input_mask

        # Writing the output result
        write_img(output_path, masked_data)

    else:
        print("ERROR: not the same label as input data: " + data_name + " data compared to " + mask_name + " mask")

    return


# =============================================================================================





# =============================================================================================
# Executions

# Command to system
input_data_folder = os.path.abspath(sys.argv[1])
input_mask_folder = os.path.abspath(sys.argv[2])
output_folder = os.path.abspath(sys.argv[3])

print("Starting mask_sub_regions...")
print("input_data_folder:", input_data_folder)
print("input_mask_folder:", input_mask_folder)
print("output_folder:", output_folder)

print("Processing...")
input_data_list = [f for f in os.listdir(input_data_folder) if f.endswith(".nrrd")]
input_data_path_list = [os.path.join(input_data_folder, f) for f in input_data_list]
input_data_path_list = sorted(input_data_path_list)
input_mask_list = [f for f in os.listdir(input_mask_folder) if f.endswith(".nrrd")]
input_mask_path_list = [os.path.join(input_mask_folder, f) for f in input_mask_list]
input_mask_path_list = sorted(input_mask_path_list)
output_path = [os.path.join(output_folder, f.split(".")[0] + "_masked.nrrd") for f in input_data_list]
output_path = sorted(output_path)
nb_files = len(input_data_list)

print("input_data_list", len(input_data_list))
# print(input_data_list)
print("input_mask_path_list", len(input_mask_path_list))
# print(input_mask_list)
print("output_path", len(output_path))
# print(output_path)

used_cpu = int(mp.cpu_count()/2)
print("Starting parallel computing on " + str(used_cpu) + " nodes")
pool = mp.Pool(used_cpu)
pool.starmap(mask_sub_regions, [(input_data_path_list[i], input_mask_path_list[i], output_path[i]) for i in range(nb_files)])
pool.close()
print("Done: Sub-regions successfully masked")
# =============================================================================================
