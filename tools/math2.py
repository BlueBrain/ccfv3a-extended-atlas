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


def RGB2GS(RGB_array = []):
    """
    Converting a RGB array into a grayscale array according to the sRGB standard norm
    @method RGB2GS
    @param {String} RGB_array The RGB array to be converted into Grayscale values
    @return {Array} An array with all the converted values from RGB_array in grayscale values
    """

    R, G, B = RGB_array[:,:,:,0], RGB_array[:,:,:,1], RGB_array[:,:,:,2]

    # The sRGB standard norm
    GS_img = 0.2126*R + 0.7152*G + 0.0722*B

    # The luminosity method
    # GS_img = 0.299*R + 0.587*G + 0.114*B

    return GS_img



def img_normalization(img_array = []):
    """
    Normalizing image value between 0 and 1
    @method img_normalization
    @param {Array} img_array The input array to be normalized between 0 and 1
    @return {Array} An array with all the values from img_array normalized between 0 and 1
    """

    normalized_img = img_array / np.linalg.norm(img_array)

    return normalized_img



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
        print("ERROR: img_path " + ext + " file format not supported")
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



def math_two_images(input_img1_path = "", input_img2_path = "", output_img_path = "", operation = ""):
    """
    Apply mathematical calculations between two images
    @method math
    @param {String} input_img1_path The path of the first input image
    @param {String} input_img2_path The path of the second input
    @param {String} operation The operation to applied between the two images
    @return {None} Writes the result of the operation between the two input images
    """

    # Reading the input volume
    print("READ IMAGE 1")
    input_img1 = read_img(input_img1_path)
    print("READ IMAGE 2")
    input_img2 = read_img(input_img2_path)
    
    # Substracting the two slices
    if operation == "-":
        print("operation = [IMG1] - [IMG2]")
        output_img = input_img1 - input_img2

    # Substracting the two slices using absolute difference
    elif operation == "abs-":
        print("operation = abs([IMG1] - [IMG2])")
        output_img = abs(input_img1 - input_img2)

    # Adding the two images
    elif operation == "+":
        print("operation = [IMG1] + [IMG2]")
        output_img = input_img1 + input_img2

    # Multiplying the two images term to term
    elif operation == ".x":
        print("operation = [IMG1] .x [IMG2]")
        if input_img1.shape == input_img2.shape:
            output_img = input_img1 * input_img2
        else:
            print("ERROR: Inconsistant volume dimensions: " + str(input_img1.shape) + " != " + str(input_img2.shape))
            return

    # Multiplying the two images using matricial operations
    elif operation == "x":
        print("operation = [IMG1] x [IMG2]")
        if input_img1.shape == np.transpose(input_img2).shape:
            output_img = np.matmut(input_img1, input_img2)
        else:
            print("ERROR: Inconsistant volume dimensions: " + str(input_img1.shape) + " != " + str(np.transpose(input_img2).shape))
            return

    # Dividing the two images term to term
    elif operation == "./":
        print("operation = [IMG1] ./ [IMG2]")
        if input_img1.shape == input_img2.shape:
            output_img = input_img1 / input_img2
        else:
            print("ERROR: Inconsistant volume dimensions: " + str(input_img1.shape) + " != " + str(input_img2.shape))
            return

    elif operation == "average":
        print("operation = ([IMG1] + [IMG2]) / 2")
        if input_img1.shape == input_img2.shape:
            output_img = (input_img1 + input_img2)/2
        else:
            print("ERROR: Inconsistant volume dimensions: " + str(input_img1.shape) + " != " + str(input_img2.shape))
            return

    elif operation == "average_mask":
        print("operation = ([IMG1[!=0]] + [IMG2[!=0]]) / 2")
        if input_img1.shape == input_img2.shape:
            common_non_zero_indices = np.logical_and(input_img1 != 0, input_img2 != 0)
            average_non_zero_values = (input_img1[common_non_zero_indices] + input_img2[common_non_zero_indices]) / 2
            output_img = np.zeros_like(input_img1)
            output_img[common_non_zero_indices] = average_non_zero_values
            coord1 = np.where((input_img2 == 0) & (input_img1 != 0))
            coord2 = np.where((input_img1 == 0) & (input_img2 != 0))
            output_img[coord1] = input_img1[coord1]
            output_img[coord2] = input_img2[coord2]
        else:
            print("ERROR: Inconsistant volume dimensions: " + str(input_img1.shape) + " != " + str(input_img2.shape))
            return

    else:
        print("ERROR: Operation " + operation + " not known")
        return

    # Writing the result
    write_img(output_img_path, output_img)

    return

# =============================================================================================




# =============================================================================================
# Exectutions

# Command to system
input_img1_path = os.path.abspath(sys.argv[1])
input_img2_path = os.path.abspath(sys.argv[2])
output_img_path = os.path.abspath(sys.argv[3])
operation = (sys.argv[4])

print("Starting math_two_images...")
print("input_img1_path:", input_img1_path)
print("input_img2_path:", input_img2_path)
print("output_img_path:", output_img_path)
print("operation:", operation)

print("Processing...")
math_two_images(input_img1_path, input_img2_path, output_img_path, operation)
print("Done: operation successfully applied to slices")

# =============================================================================================
