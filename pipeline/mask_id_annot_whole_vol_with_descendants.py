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




def mask_id_annot(input_annot_file_path = "", input_annatomical_data_path = "", input_hier_id_folder = "", output_mask_folder = "", output_masked_annat_folder = ""):
    """
    Identifying the ID hierarchy 
    @method mask_id_annot
    @param {String} input_annot_file_path The path of the input anntation file
    @param {String} input_annatomical_data_path The path of the anatomical file corresponding the the annotation file
    @param {String} input_hier_id_folder The path of the input hierarchy id folder
    @param {String} output_mask_folder The path of the output folder where to save the masks
    @param {String} output_masked_annat_folder The path of the output folder where to save the anatomical volumes masked
    @return {None} Writes the masked files with only the ids that have been selected
    """

    # Reading the input file
    annot_vol = read_img(input_annot_file_path)
    annot_vol_dim = annot_vol.shape
    annat_vol = read_img(input_annatomical_data_path)
    id_list_full = [f for f in os.listdir(input_hier_id_folder)]

    # Setting all values to 0 except those in id_list that are set to 1
    for id in id_list_full:
        print("id:", id)
        id_list = read_img(os.path.join(input_hier_id_folder, id))
        for i in range(len(id_list)):
            print("Processing id_nb " + str(i + 1) + "/" + str(len(id_list)) + "   |   ID " + str(id_list[i]))

            # Checking if aloredaay exists
            output_masked_annat = os.path.join(output_masked_annat_folder, str(id_list[i]) + "_masked.nrrd")
            if os.path.exists(output_masked_annat):
                print("Skip: ID " + str(id_list[i]) + " already exists")
                pass
            else:
                # Creation of the mask
                output_mask = np.zeros(annot_vol_dim, dtype="float32")
                output_mask[np.isin(annot_vol, id_list[i])] = 1

                # Masking the anatomical data
                masked_anat = annat_vol * output_mask

                # Writing of the output images
                output_mask_path = os.path.join(output_mask_folder, str(id_list[i]) + "_mask.nrrd")
                write_img(output_mask_path, output_mask)
                output_masked_annat = os.path.join(output_masked_annat_folder, str(id_list[i]) + "_masked.nrrd")
                write_img(output_masked_annat, masked_anat)

    return


# =============================================================================================





# =============================================================================================
# Executions

# Command to system
input_annot_file_path = os.path.abspath(sys.argv[1])
input_annatomical_data_path = os.path.abspath(sys.argv[2])
input_hier_id_folder = os.path.abspath(sys.argv[3])
output_mask_folder = os.path.abspath(sys.argv[4])
output_masked_annat_folder = os.path.abspath(sys.argv[5])


print("Starting mask_id_annot_whole_vol...")
print("input_annot_file_path:", input_annot_file_path)
print("input_annatomical_data_path:", input_annatomical_data_path)
print("input_hier_id_folder:", input_hier_id_folder)
print("output_mask_folder:", output_mask_folder)
print("output_masked_annat_folder:", output_masked_annat_folder)

print("Processing...")
mask_id_annot(input_annot_file_path, input_annatomical_data_path, input_hier_id_folder, output_mask_folder, output_masked_annat_folder)
print("Done: annotation file successfully masked with id values")
# =============================================================================================
