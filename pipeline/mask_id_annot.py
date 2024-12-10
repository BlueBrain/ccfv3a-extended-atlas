#!/usr/bin/python
# -*- coding: latin-1 -*-



# =============================================================================================
# Librairies importation

import numpy as np
import nrrd
import sys
import os

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




def mask_id_annot(input_annot_file_path = "", ex = "", output_file_path = ""):
    """
    Identifying the ID hierarchy 
    @method mask_id_annot
    @param {String} input_annot_file_path The path of the input anntation file
    @param {String} input_hier_id_file_list The path of the input hierarchy id 
    @param {String} output_file_path The path of the output mask file to be written
    @return {None} Writes the masked file with only the ids that have been selected
    """

    # Reading the input file
    annot_vol = read_img(input_annot_file_path)
    annot_vol_dim = annot_vol.shape
    id_list = read_img(input_hier_id_file_list)
    print("dtype:", annot_vol.dtype)

    # Setting all values to 0 except those in id_list that are set to 1
    output_vol = np.zeros(annot_vol_dim, dtype=annot_vol.dtype)
    # for id in id_list:
    #     coord = np.where(annot_vol == id)
    #     output_vol[coord] = 1
    output_vol[np.isin(annot_vol, id_list)] = 1

    # Writing the output result
    write_img(output_file_path, output_vol)

    return


# =============================================================================================





# =============================================================================================
# Executions

# Command to system
input_annot_file_path = os.path.abspath(sys.argv[1])
input_hier_id_file_list = os.path.abspath(sys.argv[2])
output_file_path = os.path.abspath(sys.argv[3])

print("Starting mask_id_annot...")
print("input_annot_file_path:", input_annot_file_path)
print("input_hier_id_file_list:", input_hier_id_file_list)
print("output_file_path:", output_file_path)

print("Processing...")
mask_id_annot(input_annot_file_path, input_hier_id_file_list, output_file_path)
print("Done: annotation file successfully masked with id values")
# =============================================================================================
