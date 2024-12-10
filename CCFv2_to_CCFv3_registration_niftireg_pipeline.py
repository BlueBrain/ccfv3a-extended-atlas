#!/usr/bin/python
# -*- coding: latin-1 -*-



# =============================================================================================
# Librairies importation

import numpy as np
import nrrd
import sysB
import os
import ants
from atlannot.ants import register, transform
from scipy.stats import entropy
import csv
from nipype.interfaces import niftyreg

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



def create_zero_vol(img = []):
    """
    Creating an empty img with the input image dimensions (only filled with zeros)
    @method create_zero_vol
    @param {NumpyArray} img The image from which to create a zero array with its dimensions
    @return {Array} An array with zero values in the img dimensions
    """

    dim = img.shape
    zeros_img = np.full([dim[0], dim[1], dim[2]], 0)

    return zeros_img


def write_CSV(csv_file_path = "", list_2bewritten = []):
    """
    Writing a list in a CSV file
    @method write_CSV
    @param {String} csv_file_path The path of the output CSV file to be written
    @param {List} list_2bewritten The list to be written into the CSV file
    @return {None} Writes a CSV file with list_2bewritten at csv_file_path
    """

    f = open(csv_file_path, 'w+')
    w = csv.writer(f)
    w.writerow(list_2bewritten)
    w = None
    f.close()
    f = None
    print("CSV file successfully written at path " + csv_file_path)

    return



def registration_inftireg_F3D(input_fixed_img = [], input_moving_img = []):
    node = niftyreg.RegF3D()
    node.inputs.ref_file = os.path.abspath(input_fixed_img)
    node.inputs.flo_file = os.path.abspath(input_moving_img)
    print(node.cmdline)
    node.run()


def slice2slice_registration_antspy(input_fixed_vol_path = "", input_moving_vol_path = "", output_vol_path = "", output_df_path = "", incidence = "", deformation_field = "yes", type_of_transform = "SyN"):
    """
    Computing the slice-to-slice registration between two volumes
    @method slice2slice_registration_antspy
    @param {String} input_fixed_vol_path The path of the input fixed volume
    @param {String} input_moving_vol_path The path of the input moving volume
    @param {String} output_vol_path The path of the output registered moving image
    @param {String} incidence The incidence to consider
    @param {String} incidence The incidence to consider
    @param {String} type_of_transform The transformation type to be applied
    @return {None} Writes the output registered moving image at output_vol_path
    """

    # Reading the input volumes and getting their dimensions
    input_fixed_vol = read_img(input_fixed_vol_path)
    input_moving_vol = read_img(input_moving_vol_path)
    dim_fixed_vol= input_fixed_vol.shape
    dim_moving_vol = input_moving_vol.shape

    # Calculating the slice-to-slice similarity
    if dim_fixed_vol != dim_moving_vol:
        print("ERROR: dimensions of the two volumes missmatch")
        return
    else:
        registered_output_vol = create_zero_vol(input_fixed_vol)
        # df_output_vol = create_zero_vol(input_fixed_vol)
        df_output_vol = []

        # Parameters for registration
        reg_terations = (40, 20, 0) # Vector of iterations for SyN
        aff_metric = "mattes" # {GC, mattes, meansquares} The metric for the affine part
        syn_metric = "mattes" # {CC, mattes, meansquares, demons} The metric for the SyN part
        Verbose = False # Verbose
        initial_transform = None # Transforms to prepend the before the registration

        if incidence == "coronal":
            for i in range(dim_fixed_vol[0]):
                print("Warping slice " + str(i + 1) + "/" + str(dim_fixed_vol[0]))
                fixed_img = input_fixed_vol[i,:,:].astype("float32")
                moving_img = input_moving_vol[i,:,:].astype("float32")
                if np.all(moving_img == 0) or np.all(fixed_img == 0):
                    print("ZERO image")
                    reg_moving_img = np.full([dim_fixed_vol[1], dim_fixed_vol[2]], 0)
                    # df_mov2ref = np.full([80,114,1,1,2], 0)
                    df_mov2ref = np.full([160,228,1,1,2], 0)
                else:
                    # Estimating the displacement field
                    df_mov2ref, _ = antspy_registration(fixed_img, moving_img, type_of_transform, reg_terations, aff_metric, syn_metric, Verbose, initial_transform)
                    # Warping the moving image using the displacement field
                    reg_moving_img = df_mov2ref.warp(moving_img)
                    # reg_moving_img = registration_antspy_loc(fixed_img, moving_img)
                    # df_mov2ref = register(fixed_img.astype(np.float32), moving_img.astype(np.float32), type_of_transform = type_of_transform)
                registered_output_vol[i, :, :] = reg_moving_img

        else:
            print("ERROR: Incidence " + incidence + " does not exist")
            return

    # Writing the result
    write_img(output_vol_path, registered_output_vol.astype(np.float32))
    # df_output_vol = np.array(df_output_vol)
    # print(df_output_vol.shape)
    # print(df_output_vol)
    # write_img(output_df_path, df_output_vol)#.astype(np.float32))

    return registered_output_vol.astype(np.float32)



def normalized_mutual_information(image1, image2, nbins=256):
    # Calculate joint histogram
    hist_2d, _, _ = np.histogram2d(image1.flatten(), image2.flatten(), bins=nbins)

    # Calculate marginal histograms
    hist_1d_image1, _ = np.histogram(image1, bins=nbins)
    hist_1d_image2, _ = np.histogram(image2, bins=nbins)

    # Compute entropy of marginal histograms
    entropy_image1 = entropy(hist_1d_image1)
    entropy_image2 = entropy(hist_1d_image2)

    # Compute joint entropy
    joint_entropy = entropy(hist_2d.flatten())

    # Compute mutual information
    mutual_information = entropy_image1 + entropy_image2 - joint_entropy

    # Compute normalized mutual information
    normalized_mutual_information = mutual_information / np.sqrt(entropy_image1 * entropy_image2)

    return normalized_mutual_information


# =============================================================================================




# =============================================================================================
# Exectutions

# Command to system
input_fixed_vol_path = os.path.abspath(sys.argv[1])
input_moving_vol_path = os.path.abspath(sys.argv[2])
output_folder = os.path.abspath(sys.argv[3])
incidence = sys.argv[4]
deformation_field = sys.argv[5]
type_of_transform = sys.argv[6]

print("Starting CCFv2_to_CCFv3_registration_pipeline...")
print("input_fixed_vol_path:", input_fixed_vol_path)
print("input_moving_vol_path:", input_moving_vol_path)
print("output_folder:", output_folder)
print("incidence:", incidence)
print("deformation_field:", deformation_field)
print("type_of_transform", type_of_transform)

print("Processing...")

# Initializing variables
nmi_list = []
fixed_img, hd = nrrd.read(input_fixed_vol_path)

# STEP 01: 3D initialization
print("\nSTEP 01: 3D initialization")
output_vol_path = os.path.join(output_folder, "STEP01_nissl2template_3D.nrrd")
output_df_path = os.path.join(output_folder, "STEP01_nissl2template_3D_df.nrrd")
registration_antspy(input_fixed_vol_path, input_moving_vol_path, output_vol_path, output_df_path, deformation_field, "nrrd", "Affine")
moving_processed_img = read_img(output_vol_path)
nmi_calc_1 = normalized_mutual_information(fixed_img, moving_processed_img)
nmi_list.append(nmi_calc_1)
print("NMI =", round(nmi_calc_1, 3))

# STEP 02: 2D COR initialization
print("\nSTEP 02: 2D COR initialization")
old_output_vol_path = os.path.join(output_folder, "STEP02_nissl2template_2D_COR.nrrd")
new_output_df_path = os.path.join(output_folder, "STEP02_nissl2template_2D_COR_df.nrrd")
slice2slice_registration_antspy(input_fixed_vol_path, output_vol_path, old_output_vol_path, new_output_df_path, incidence, deformation_field, type_of_transform)
moving_processed_img = read_img(old_output_vol_path)
nmi_calc_2 = normalized_mutual_information(fixed_img, moving_processed_img)
nmi_list.append(nmi_calc_2)
print("NMI =", round(nmi_calc_2, 3))

# Setting parameters
i = 2
mode = 1
names = ["_", "3D", "2D_COR"]

# Loop NMI dependant
while round(nmi_calc_2,3) > round(nmi_calc_1,3):
    i += 1
    # Output pathes definition
    output_vol_name = "STEP%02d" % i + "_nissl2template_" + names[mode] + ".nrrd"
    output_df_name = "STEP%02d" % i + "_nissl2template_" + names[mode] + "_df.nrrd"
    output_vol_path = os.path.join(output_folder, output_vol_name)
    output_df_path = os.path.join(output_folder, output_df_name)
    if os.path.exists(output_vol_path):
        reg_img = read_img(old_output_vol_path)
        nmi_calc_2 = normalized_mutual_information(fixed_img, reg_img)
        nmi_list.append(nmi_calc_2)
    else:
        print("\nSTEP %02d" % i + ": " + names[mode] + " registration")

        # 3D registration
        if mode == 1:
            reg_img = registration_antspy(input_fixed_vol_path, old_output_vol_path, output_vol_path, output_df_path, deformation_field, "nrrd", type_of_transform)
            mode = 2

        # 2D CORONAL registration
        elif mode == 2:
            reg_img = slice2slice_registration_antspy(input_fixed_vol_path, old_output_vol_path, output_vol_path, output_df_path, incidence, deformation_field, type_of_transform)
            mode = 1

        nmi_calc_1 = nmi_list[-1]
        nmi_calc_2 = normalized_mutual_information(fixed_img, reg_img)
        print("NMI =", round(nmi_calc_2, 3))
        nmi_list.append(nmi_calc_2)
        old_output_vol_path = output_vol_path

csv_path = os.path.join(output_folder, "nmi_values_list.csv")
write_CSV(csv_path, nmi_list)

print("Done: registration pipeline process was run " + str(i) + " times.")


# =============================================================================================
