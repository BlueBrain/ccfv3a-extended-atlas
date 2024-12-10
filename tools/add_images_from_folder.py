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



def RGB2GS(input_RGB_img = ""):
    """
    Converting a RGB array into a grayscale array according to the sRGB standard norm
    @method RGB2GS
    @param {String} input_RGB_img The path of the input RGB image to be converted
    @return {None} Writes the output converted GS image at output_GS_img_path
    """

    # Splitting the channels
    R, G, B = input_RGB_img[:,:,:,0], input_RGB_img[:,:,:,1], input_RGB_img[:,:,:,2]

    # The sRGB standard norm
    GS_img = 0.2126*R + 0.7152*G + 0.0722*B

    return GS_img




def add_images_from_folder(input_folder = "", output_vol_path = 0):
    """
    Adding all images from a folder
    @method add_images_from_folder
    @param {String} input_folder The path of the input folder where to find the files to be added
    @param {String} output_vol_path The path of the output file to be written
    @return {None} Writes the output added file
    """

    # Reading the input files
    file_list = [f for f in os.listdir(input_folder) if f.endswith(".nrrd") or f.endswith(".npy")]
    path_list = [os.path.join(input_folder, f) for f in file_list]
    first_img = read_img(path_list[0])
    dim = first_img.shape

    # Creating the ouptut empty vol
    ouptut_vol = np.zeros([dim[0], dim[1], dim[2]])

    # Adding all files
    for i in range(len(path_list)):
        print("Adding image " + str(i+1) + "/" + str(len(path_list)) + "  |  " + path_list[i].split("/")[-1])
        img = read_img(path_list[i])
        if len(img.shape) == 4:
            img = RGB2GS(img)
        else:
            pass
        ouptut_vol += img

    # Writing the output file
    write_img(output_vol_path, ouptut_vol)

    return


# =============================================================================================





# =============================================================================================
# Executions

# Command to system
input_folder = os.path.abspath(sys.argv[1])
output_vol_path = os.path.abspath(sys.argv[2])

print("Starting add_images_from_folder...")
print("input_folder:", input_folder)
print("output_vol_path:", output_vol_path)

print("Processing...")
add_images_from_folder(input_folder, output_vol_path)
print("Done: Files in the input folder successfully added")
# =============================================================================================
