#!/usr/bin/python
# -*- coding: latin-1 -*-



# =============================================================================================
# Librairies importation

import numpy as np
import nrrd
import atlalign as atl
from atlalign.non_ml.intensity import antspy_registration
from atlannot.ants import register, transform
import sys
import re
import os
import nibabel as nib

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
    Writing a NPY or NRRD or NIFTI file
    @method write_img
    @param {String} img_path The path of the image to be written (NPY or NRRD)
    @param {Array} out_array_img The array to be written at img_path
    @return {None} Writes the out_array_img at img_path
    """

    ext = img_path.split(".")[-1]
    out_array_img = np.array(out_array_img)

    if ext == "nrrd":
        print("NRRD")
        try:
            nrrd.write(img_path, out_array_img.astype("float32"))
            nrrd.write(img_path, out_array_img)
        except AttributeError:
            nrrd.write(img_path, out_array_img)
        except ValueError:
            out_array_img = out_array_img.astype(np.float32)
            nrrd.write(img_path, out_array_img)

    elif ext == "npy":
        print("NPY")
        try:
            np.save(img_path, out_array_img.astype("float32"))
        except ValueError:
            np.save(img_path, out_array_img)

    elif ext == "nii" or ext == "gz":
        print("NII")
        dim = np.array(out_array_img.shape)
        print(dim)
        # out_img = nib.Nifti1Image(out_array_img, np.eye(*(dim+1)))
        out_img = nib.Nifti1Image(out_array_img, np.eye(4,4))
        # nib.save(out_img.astype("float32"), img_path)
        nib.save(out_img, img_path)

    elif ext == "png":
        print("PNG")
        data_min = np.min(out_array_img)
        data_max = np.max(out_array_img)
        data_norm = (out_array_img - data_min) * 255 / (data_max - data_min)
        data_norm = data_norm.astype(np.uint8)
        imageio.imwrite(img_path, data_norm)

    elif ext == "jpg":
        print("JPG")
        cv2.imwrite(img_path, out_array_img)

    else:
        print("ERROR: outuput file format not supported")
        return

    print("Image successfully written at path", img_path)

    return



def registration_antspy(fixed_img_path = "", moving_img_path = "", output_folder = "", deformation_field = "no", file_format = "npy", type_of_transform = "SyN", syn_metric = "mattes", interpolator = "linear"):
    """
    Calculating the displacement field between a fixed and a moving image and apply it to the moving image (warping)
    @method df_estimation_antspy
    @param {String} fixed_img_path The path of the input fixed image (NPY or NRRD)
    @param {String} moving_img_path The path of the input moving image (NPY or NRRD)
    @param {Bool} deformation_field If the deformation field is written or not
    @param {String} output_folder The output folder where to write the output files
    @param {String} file_format The output warped image file format
    @param {String} type_of_transform The selected registration type from ANTspy \
                    {Translation, Rigid, Similarity, QuickRigid, DenseRigid, BOLDRigid, Affine,\
                     AffineFast, BOLDRigid, Affine, TRSAA, ElasticSyN, SyN, SyNRA, \
                     SyNOnly, SyNCC, SyNabp, SyNBold, SyNBoldAff, SyNAggro, TVMSQ, TVMSQC}
    @param {String} syn_metric The selected metric for SyN registration \
                    {CC, mattes, meansquares, demons}
    @param {String} interpolator The selected interpolation for the application of the transform function \
                    {linear, genericLabel}
    @return {None} Writing the output warped image (and optionnally the deformation field)
    """

    # Reading the input images
    fixed_img = read_img(fixed_img_path)
    moving_img = read_img(moving_img_path)
    fixed_img_dim = fixed_img.shape
    moving_img_dim = moving_img.shape
    moving_img_name = moving_img_path.split("/")[-1].split(".")[0]


    if fixed_img_dim != moving_img_dim:
        print("ERROR: Dimensions of the volumes mismatch: " + str(moving_img_dim) + " TO " + str(fixed_img_dim))
        return

    elif len(fixed_img_dim) == 2:
        # Setting the parameters of the function
        reg_terations = (40, 20, 0) # Vector of iterations for SyN
        aff_metric = "mattes" # {GC, mattes, meansquares} The metric for the affine part
        # syn_metric = "mattes" # {CC, mattes, meansquares, demons} The metric for the SyN part
        Verbose = False # Verbose
        initial_transform = None # Transforms to prepend the before the registration

        # Registration estimation
        if deformation_field == "yes":
            # Getting the displacement field
            df_mov2ref = antspy_registration(fixed_img, moving_img, type_of_transform, reg_terations, aff_metric, syn_metric, Verbose, initial_transform, output_folder)
        else:
            pass

        # Estimating the displacement field
        df_mov2ref, _ = antspy_registration(fixed_img, moving_img, type_of_transform, reg_terations, aff_metric, syn_metric, Verbose, initial_transform)

        # Warping the moving image using the displacement field
        reg_img = df_mov2ref.warp(moving_img)

    elif len(fixed_img_dim) == 3:

        # Estimating the displacement field
        df_mov2ref = register(fixed_img.astype(np.float32), moving_img.astype(np.float32), type_of_transform = type_of_transform, reg_terations = (40, 20, 0), syn_metric = syn_metric)

        # Warping the moving image using the displacement field
        reg_img = transform(moving_img.astype(np.float32), df_mov2ref, interpolator = interpolator)
    else:
        print("ERROR: input image dimensions " + str(fixed_img_dim) + " and/or " + str(moving_img_dim) + " not handled")
        return

    # Writing the output warped moving image
    output_mov_img_path = os.path.join(output_folder, moving_img_name + "_" + type_of_transform +  "." + file_format)
    write_img(output_mov_img_path, reg_img)

    # Writing the deformation field
    if deformation_field == "yes":
        df_mov2ref_output_path = output_mov_img_path.replace(type_of_transform + "." + file_format, type_of_transform + "_df.npy")
        write_img(df_mov2ref_output_path, df_mov2ref)

    return


# =============================================================================================




# =============================================================================================
# Executions

# Command to system
input_fixed_img = os.path.abspath(sys.argv[1])
input_moving_img = os.path.abspath(sys.argv[2])
output_folder = os.path.abspath(sys.argv[3])
deformation_field = sys.argv[4]
file_format = sys.argv[5]
try:
    type_of_transform = sys.argv[6]
except:
    type_of_transform = "SyN"
    pass
try:
    syn_metric = sys.argv[7]
except:
    syn_metric = "mattes"
    pass
try:
    interpolator = sys.argv[8]
except:
    interpolator = "linear"
    pass

print("Starting registration_antspy...")
print("input_fixed_img:", input_fixed_img)
print("input_moving_img:", input_moving_img)
print("output_folder:", output_folder)
print("deformation_field:", deformation_field)
print("file_format:", file_format)
print("type_of_transform:", type_of_transform) # Rigid, Affine, SyN, SyNAggro
print("syn_metric:", syn_metric) # mattes, demons
print("interpolator:", interpolator) # linear, nearest


print("Processing...")
registration_antspy(input_fixed_img, input_moving_img, output_folder, deformation_field, file_format, type_of_transform, syn_metric, interpolator)
print("Done: Moving image successfully warped to fixed image")

# =============================================================================================
