#!/usr/bin/python
# -*- coding: latin-1 -*-



# =============================================================================================
# Librairies importation

import numpy as np
import nrrd
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
        try:
            img = np.load(img_path)
        except ValueError:
            img = np.load(img_path, allow_pickle=True)
    elif ext == "nii" or ext == "gz":
        nii_image = nib.load(img_path)
        img = np.array(nii_image.dataobj)
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
    elif ext == "gz":
        img = nib.Nifti1Image(out_array_img, np.eye(4))
        nib.save(img, img_path)
    else:
        print("ERROR: outuput file format not supported")
        return

    print("Image successfully written at path", img_path)

    return


def apply_def_field(ref_img_path = "", moving_img_path = "", deformation_field_path = "", output_reg_img = "", interpolator = ""):
    """
    Applying a deformation field to a moving image
    @method apply_def_field
    @param {String} ref_img_path The path of the input reference image (NPY or NRRD)
    @param {String} moving_img_path The path of the input moving image (NPY or NRRD)
    @param {Bool} deformation_field The path of the deformation field to be applied
    @param {String} output_reg_img The path of the output registered image
    @param {String} interpolator The interpolator mode to use ("genericLabel" for altases, "linear" otherwise)
    @return {None} Writing the output warped image
    """

    # Applying the deformation field to the moving image
    if deformation_field_path.split(".")[-1] == "gz" or deformation_field_path.split(".")[-1] == "nii":
        from nipype.interfaces import niftyreg
        # def_field = nib.load(deformation_field_path)
        # def_field = def_field.dataobj
        # reg_img = transform(moving_img.astype(np.float32), def_field, interpolator = interpolator)
        node = niftyreg.RegF3D()
        node.inputs.ref_file = ref_img_path
        node.inputs.flo_file = moving_img_path
        node.inputs.incpp_file = deformation_field_path
        node.inputs.res_file = output_reg_img
        print(node.cmdline)
        node.run()

    else:
        # Librairies importation
        import atlalign as atl
        from atlalign.non_ml.intensity import antspy_registration
        from atlannot.ants import register, transform

        # Reading the input images
        moving_img = read_img(moving_img_path)
        deformation_field = read_img(deformation_field_path)
        reg_img = transform(moving_img.astype(np.float32), deformation_field, interpolator = interpolator)

        # Writing the output warped moving image
        write_img(output_reg_img, reg_img)

    return


# =============================================================================================




# =============================================================================================
# Executions

# Command to system
ref_img_path = os.path.abspath(sys.argv[1])
moving_img_path = os.path.abspath(sys.argv[2])
deformation_field_path = os.path.abspath(sys.argv[3])
output_reg_img = os.path.abspath(sys.argv[4])
interpolator = sys.argv[5]

print("Starting apply_def_field...")
print("reference_img_path:", moving_img_path)
print("moving_img_path:", moving_img_path)
print("deformation_field_path:", deformation_field_path)
print("output_reg_img:", output_reg_img)
print("interpolator:", interpolator)

print("Processing...")
apply_def_field(ref_img_path, moving_img_path, deformation_field_path, output_reg_img, interpolator)
print("Done: Deformation field successsfully applied to the moving image")

# =============================================================================================
