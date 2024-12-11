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




def bounding_box(input_vol_path = "", output_vol_path = ""):
    """
    Identifies the bounding box of a volume corresponding to where it is different from zero
    @method bounding_box
    @param {String} input_vol_path The path of the input volume
    @param {String} output_vol_path The path of the output volume
    @return {None} Writes the output volume with only data in bounding box
    """

    # Reading the input image
    input_vol = read_img(input_vol_path)
    
    # Processing bounding box
    if len(input_vol.shape) == 2:
        coord = np.where(input_vol != 0)

        # Determine min coord
        x_min = np.min(coord[0])
        x_min_coord = np.where(coord[0] == x_min)
        y_min = np.min(coord[1][x_min_coord])

        # Determine max coord
        x_max = np.max(coord[0])
        x_max_coord = np.where(coord[0] == x_max)
        y_max = np.max(coord[1][x_max_coord])

        # Identify the output vol
        output_vol = input_vol[x_min:x_max, y_min:y_max]

    elif len(input_vol.shape) == 3:
        coord = np.where(input_vol != 0)

        # Determine min coord
        z_min = np.min(coord[0])
        z_min_coord = np.where(coord[0] == z_min)
        y_min = np.min(coord[1][z_min_coord])
        y_min_coord = np.where(coord[1] == y_min)
        x_min = np.min(coord[2][y_min_coord])

        # Determine max coord
        z_max = np.max(coord[0])
        z_max_coord = np.where(coord[0] == z_max)
        y_max = np.max(coord[1][z_max_coord])
        y_max_coord = np.where(coord[1] == y_max)
        x_max = np.max(coord[2][y_max_coord])

        # Identify the output vol
        output_vol = input_vol[z_min:z_max, y_min:y_max, x_min:x_max]

    # Writing the output result
    write_img(output_vol_path, output_vol)

    return



# =============================================================================================





# =============================================================================================
# Executions

# Command to system
input_vol_path = os.path.abspath(sys.argv[1])
output_vol_path = os.path.abspath(sys.argv[2])

print("Starting bounding_box...")
print("input_vol_path:", input_vol_path)
print("output_vol_path:", output_vol_path)

print("Processing...")
bounding_box(input_vol_path, output_vol_path)
print("Done: Bounding boxes successfully identifies and written")
# =============================================================================================
