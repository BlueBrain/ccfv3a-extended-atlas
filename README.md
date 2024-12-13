# ccfv3a-extended-atlas

# Overview
This repository contains the code developed for producing the CCFv3aBBP Nissl-based atlas, an extension of the Allen Institute's Common Coordinate Framework version 3 (CCFv3).
The project focuses on enhancing the anatomical correspondance between the Allen Reference Atlas (ARA) Nissl stained volume and the CCFv3 annotations and integrate the necessary data (anatomy and annotation) to provide a comprehensive atlas of the entire mouse brain.
This new atlas version extends the main olfactory bulb, cerebellum, and medulla regions. Some additional layers are also incorporated within the resulting CCFv3cBBP version, such as the barrel columns and the spinal cord.
This project also made it possible to produce an average Nissl template based on 734 mouse brains.
The pipeline and the tools provided in that repository gathers several alignment-based methods for performing a region-based registration mainly, divided into 3 Automated Registration Methods (ARM):
- ARM A: Alignment of the ARA Nissl volume in the CCFv3,
- ARM B: Extension of the main olfactory bulb,
- ARM C: Extension of the cerebellum/medulla.

![Capture d’écran du 2024-12-10 15-29-53](https://github.com/user-attachments/assets/15d9a75e-ccf6-43d6-9da8-c69b0e10bd43)

# Data
All the input data can be either directly collected from the Allen Institute platform: https://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/ or downloaded from that Zenodo repository: https://zenodo.org/records/13640418. This repository also includes the output data produced by the methods.

### CCFv2
- ARA Nissl (anatomical reference) called `ara_nisslCOR.nrrd`: https://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/ara_nissl/
- CCFv2 annotation (labels) called `ccfv2_annot.nrrd`: https://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/annotation/mouse_2011/

### CCFv3
- average template (anatomical reference) called `average_template.nrrd`: https://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/average_template/
- CCFv3 annotation (labels) called `ccfv3_annot.nrrd`: https://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/annotation/ccf_2022/


# Installation
```
git clone https://github.com/BlueBrain/ccfv3a-extended-atlas.git
cd CCFv3aBBP  
pip install -r requirements.txt 
```

# Features for ARM A
All the following steps for aligning the ARA Nissl volume in the CCFv3 are part of the following pipeline. They are run on a single hemisphere (right) and the output volume is mirrorred according to the interhemispheric plane. The isotropic resolution is 25 micrometers.
![Capture d’écran du 2024-12-10 16-59-38](https://github.com/user-attachments/assets/3468bebc-7db8-4694-908e-125864c0e530)

### 1. Identify the common hierarchy
This steps allows you to identify the common identifiers in both annotation files (CCFv2 and CCFv3) according to their support (number of voxels) in both versions.
This is just a tool for letting you identify the regions of interest you will focus on, as well as the level of ontology you would choose for applying the pipeline.
In the following steps, we took the example of the regitration of the `main olfactory bulb` region, with acronym `MOB`.
```
python tools/common_hierarchy.py [...]/ccfv3_hierarchy.json [...]/ccfv2_hierarchy.json [...]/input_hier_id_file_list.json [...]/output_folder
```

### 2. Create the hierarchy file subdivision
This step allows you to focus on one single region with all its descendants.
The output file in the case of the `main olfactory bulb` example will be `MOB.npy`, corresponding to the acronym of the region, including all the identifiers of the main olfactory bulb region.
```
mkdir [...]/ids
python tools/hierarchy_id.py [...]/id main_olfactory_bulb yes no yes no
```

### 3. Run the linear and nonlinear monomodal registration with the annotation files (A1)
You can either run this step yourself using the following command line or extract the result from the first step of the `deep-atlas-pipeline` at https://github.com/BlueBrain/Deep-Atlas.
This step will produce a registered annotation file called `ccfv2_annot_SyN.nrrd`, plus the attached transformation file. This output transformation file should be applied to the ARA Nissl volume as well, then called `ara_nisslCOR_SyN.nrrd`
```
python pipeline/registration_antspy.py [...]/ccfv3_annot.nrrd [...]/ccfv2_annot.nrrd [...]/output_folder yes nrrd SyN mattes nearest
```

### 4. Create the mask of all the selected regions in the CCFv2 (A2)
Once you know all the identifiers concerned by the selected region, you can create the corresponding mask of the region in the pre-aligned CCFv2.
You can apply this mask on the anatomical file using a simple volume multiplication to produce the file corresponding to the anatomy of this only region.
```
mkdir [...]/ccfv2_masks
mkdir [...]/ccfv2_annat_masked
python pipeline/mask_id_annot.py [...]/ccfv2_annot_SyN.nrrd [...]/id/MOB.npy [...]/ccfv2_masks/ccfv2_annot_SyN_MOB.nrrd
python tools/math2 [...]/ara_nisslCOR_SyN.nrrd [...]/ccfv2_masks/ccfv2_annot_SyN_MOB.nrrd [...]/ccfv2_annat_masked/ara_nisslCOR_SyN_MOB.nrrd .x
```

### 5. Create the mask of all the selected regions in the CCFv3 (A2)
Once you know all the identifiers concerned by the region, you can create the corresponding mask of the region in the CCFv3.
You can apply this mask on the anatomical file using a simple volume multiplication to produce the file corresponding to the anatomy of this only region.
```
mkdir [...]/ccfv3_masks
mkdir [...]/ccfv3_annat_masked
python pipeline/mask_id_annot.py [...]/ccfv3_annot.nrrd [...]/id/MOB.npy [...]/ccfv3_masks/ccfv3_annot_MOB.nrrd
python [...]/average_template.nrrd [...]/ccfv3_masks/ccfv3_annot_MOB.nrrd mkdir [...]/ccfv3_annat_masked/average_template_MOB.nrrd .x
```

### 6. Run the linear and nonlinear multimodal registration on the masked anatomical files (A3)
This step aims at aligning the selected anatomical masked file between the ARA Nissl volume and the average template (i.e. from the CCFv2 to the CCFv3). You need first to convert the NRRD file into the NIFTI format.
```
mkdir [...]/registered_annat
python pipeline/registration_niftireg_regF3D.py [...]/ccfv3_annat_masked/average_template_MOB.nii.gz [...]/ccfv2_annat_masked/ara_nisslCOR_SyN_MOB.nii/gz [...]/registered_annat/ara_nisslCOR_SyN_MOB_res.nii.gz
```

### 7. Mask all the output files (A4)
Once you did this registration for all the regions of interest at the level of ontolgy you chose and stored in the `[...]/registered_annat` folder, you can mask all the resulting anatomical files.
```
mkdir [...]/registered_annat_masked
python pipeline/mask_subregions_folder.py [...]/registered_annat [...]/ccfv3_masks [...]/registered_annat_masked
```

### 8. Combine all the masked output files (A4)
This step combines all files from a given folder in adding them and results into a single volume.
```
python tools/add_images_from_folder.py [...]/registered_annat_masked [...]/reconstructed_aligned_ara_nisslCOR_SyN.nrrd
```

### 9. Run the final nonlinear monomodal registration step (A5)
This step aims at aligning the raw ARA Nissl with the reconstructed aligned ARA Nissl in the CCFv3. You also need to convert all NRRD files into the NIFTI format.
```
python pipeline/registration_niftireg_regF3D.py [...]/reconstructed_aligned_ara_nisslCOR_SyN.nii.gz [...]/ara_nisslCOR_SyN.nii.gz [...]/ara_nisslCOR_SyN_res.nii.gz
```
### Note
This method does not work for the cerebellum, which requires specific processing (see ARM C). Step A5 should only be applied once the Nissl volume has been fully reconstructed in the CCFv3 with all the independant alignments, i.e., including the results from ARM C.


# Features for ARM B
All the following steps for extended the ARA Nissl main olfactory bulb (rostral) in the CCFv3 are part of the following pipeline. They are run on a single hemisphere (right) and the output volume is mirrorred according to the interhemispheric plane. The isotropic resolution is 25 micrometers.
![Capture d’écran du 2024-12-11 08-55-01](https://github.com/user-attachments/assets/4cf784e6-6fe7-424b-8d2e-ca48c14c5328)

### 1. Run the rough linear monomodal registration (B1)
This first step aims at roughly aligning the Allen Institute for Brain Science (AIBS) Nissl data in the sagittal incidence `aibs_nisslSAG.nrrd` with the ARA Nissl `ara_nisslCOR_SyN_res.nrrd` ailgned in the CCFv3. A first step for adapting the field of view of both data is required.
```
python pipeline/registration_antspy.py [...]/ara_nisslCOR_SyN_res.nrrd [...]/aibs_nisslSAG.nrrd [...]/output_folder yes nrrd Affine mattes linear
```
This step is producing the aligned `aibs_nisslSAG_Affine.nrrd` file, plus an attached transformation file.

### 2. Create the bounding box (B2)
Once the two data are roughly aligned, you can identify the bounding box corresponding to the olfactory area region, with acronym OLF. This will produce a file with all the identifiers for the OLF region, called `OLF.npy`.
```
python tools/hierarchy_id.py [...]/id olfactory_areas yes no yes no
python pipeline/mask_id_annot.py [...]/ccfv3_annot.nrrd [...]/OLF.npy [...]/ccfv3_annot_OLF.nrrd
python tools/bounding_box.py [...]/ccfv3_annot_OLF.nrrd [...]/ccfv3_annot_OLF_bounding_box.nrrd
```

### 3. Mask the data using the bounding box (B3)
Once the bounding box is calculated, you can apply it to the two volumes.
```
python tools/math2.py [...]/ara_nisslCOR_SyN_res.nrrd [...]/ccfv3_annot_OLF_bounding_box.nrrd [...]/ara_nisslCOR_SyN_res_OLF.nrrd .x
python tools/math2.py [...]/aibs_nisslSAG_Affine.nrrd [...]/ccfv3_annot_OLF_bounding_box.nrrd [...]/aibs_nisslSAG_Affine_OLF.nrrd .x
```

### 4. Run the nonlinear monomodal registration (B4)
This step aims at aligning more precisely the two masked data together. It will produce a deformation field file `aibs_nisslSAG_Affine_OLF_SyN_df.npy`.
```
python pipeline/registration_antspy.py [...]/ara_nisslCOR_SyN_res_OLF.nrrd [...]/aibs_nisslSAG_Affine_OLF.nrrd [...]/output_folder yes nrrd SyN mattes linear
```

### 5. Apply the deformation field to the non masked data (B5)
Once the deformation field is calculated, you can apply it to the non masked data.
```
python tools/apply_def_field.py [...]/ara_nisslCOR_SyN_res_OLF.nrrd [...]/aibs_nisslSAG_Affine.nrrd [...]/aibs_nisslSAG_Affine_OLF_SyN_df.npy [...]/aibs_nisslSAG_Affine_OLF_SyN_nonmasked.nrrd linear
```

### 6. Merge the output data (B6)
This steps aims at merging the extended and aligned olfactory bulb tissue from  `[...]/aibs_nisslSAG_Affine_SyN_nonmasked.nrrd` to `[...]/ara_nisslCOR_SyN_res.nrrd`. Several ways of performing this merging are possible. Here is one way of doing it.
```
python
import nrrd
import numpy as np
nissl_sag, _ = nrrd.read([...]/aibs_nisslSAG_Affine_OLF_SyN_nonmasked.nrrd)
nissl_cor, hd = nrrd.read([...]/ara_nisslCOR_SyN_res.nrrd)
mask_OLF, _ = nrrd.read([...]/ccfv3_annot_OLF_bounding_box.nrrd)
nissl_sag_mask = (nissl_sag*mask_OLF > 0).astype(int)
nissl_cor_mask = (nissl_cor*mask_OLF > 0).astype(int)
extension_mask = abs(nissl_sag_mask - nissl_cor_mask)
coord = np.where(extension_mask != 0)
nissl_cor[coord] = nissl_sag[coord]
nrrd.write([...]/ara_nisslCOR_SyN_res_extendedMOB.nrrd, nissl_cor, header = hd)
```

# Features for ARM C
All the following steps for extended the ARA Nissl cerebellum and medulla (caudal) in the CCFv3 are part of the following pipeline. They are run on a single hemisphere (right) and the output volume is mirrorred according to the interhemispheric plane. The isotropic resolution is 25 micrometers.
![Capture d’écran du 2024-12-11 09-50-02](https://github.com/user-attachments/assets/129dee5f-db9d-43fa-abcc-038dfc014fb0)

### 1. Run the strong monomodal nonlinear label alignment (C1)
The process will be presented for one single cerebellar lobule as an example: Flocculus with acronym FL. The following steps C1 and C2 are run independently on the sixteen cerebellar lobules with the following acronyms: Ansiform lobule Crus 1 (ANcr1), Ansiform lobule Crus 2 (ANcr2), Central lobule (II) (CENT2), Central lobule (III) (CENT3), Copula pyramidis (COPY), Culmen lobules (IV-V) (CUL4, 5), Declive (VI) (DEC), Flocculus (FL), Folium-tuber vermis (VII) (FOTU), Lingula (I) (LING), Nodulus (X) (NOD), Parafliocculus (PFL), Paramedian lobule (PRM), Pyramus (VIII) (PYR), Simple lobule (SIM), and Uvula (IX) (UVU).
```
mkdir [...]/lobule_ids
mkdir [...]/lobule_masks_ccfv2
mkdir [...]/lobule_masks_ccfv3
mkdir [...]/lobule_masks_registered
python tools/hierarchy_id.py [...]/lobule_ids Flocculus yes no yes no
python pipeline/mask_id_annot.py [...]/ccfv2_annot_SyN.nrrd [...]/lobule_ids/FL.npy [...]/lobule_masks_ccfv2/ccfv2_annot_SyN_FL.nrrd
python pipeline/mask_id_annot.py [...]/ccfv3_annot.nrrd [...]/FL.npy [...]/lobule_masks_ccfv3/ccfv3_annot_FL.nrrd
python pipeline/registration_antspy.py [...]/lobule_masks_ccfv3/ccfv3_annot_FL.nrrd [...]/lobule_masks_ccfv2/ccfv2_annot_SyN_FL.nrrd [...]/lobule_masks_registered yes nrrd SyNAggro mattes demons
```

### 2. Apply the deformation field to the corresponding anatomical file (C2)
Once the deformation field is calculated, it can be applied to the corresponding annatomical file. Repeat this step for all the sixteen lobules.
```
mkdir [...]/anatomical_lobules
mkdir [...]/anatomical_lobules_registered
python tools/math2.py [...]/ara_nisslCOR_SyN.nrrd [...]/lobule_masks_ccfv2/ccfv2_annot_SyN_FL.nrrd [...]/anatomical_lobules/ara_nisslCOR_SyN_FL.nrrd .x
python tools/apply_def_field.py [...]/lobule_masks_ccfv3/ccfv3_annot_FL.nrrd [...]/anatomical_lobules/ara_nisslCOR_SyN_FL.nrrd [...]/lobule_masks_registered/ccfv2_annot_SyN_FL_SyNAggro_df.npy [...]/anatomical_lobules_registered/ara_nisslCOR_SyN_FL_SyNAggro.nrrd
```

### 3. Reconstruct the annatomical cerebellum and incorporate it to the reconstruction from A4 (C3)
This step aims at masking and then merging all the aligned anatomical cerebellar lobules in one single volume. You can either reconstruct all the cerebellar layers in an independant file, for identifying their sublayers for instance, but you can also merge the result with all the other anatomical tissues in the CCFv3 from step A4, for then running the step A5 including all brain regions. 
```
mkdir [...]/anatomical_lobules_registered_masked
python pipeline/mask_subregions_folder.py [...]/anatomical_lobules_registered mkdir [...]/lobule_masks_ccfv3 [...]/anatomical_lobules_registered_masked
cp [...]/reconstructed_aligned_ara_nisslCOR_SyN.nrrd [...]/anatomical_lobules_registered_masked # Run this (coming from step A4) only if you want to reconstruct the entire Nissl brain in the CCFv3 for then running step A5, otherwise ignore it
python tools/add_images_from_folder.py [...]/anatomical_lobules_registered_masked [...]/reconstructed_aligned_ara_nisslCOR_SyN_CB.nrrd 
```

### 4. Extend the cerebellum and medulla and merge the results (C4-C5)
Apply the same steps from ARM B but with a bounding box including the cerebellum and the medulla independently and using the Waxholm Nissl volume in the horizontal incidence `waxh_NisslHOR.nrrd`. A first step for adapting the field of view of both data is required. You can then identify the lobule sub-layers (granular and molecular), using an Otsu thresholding for instance, on the resulting `reconstructed_aligned_ara_nisslCOR_SyN_CB.nrrd` cerebellar lobule volume.

### Note
Step A5 should be applied only once the ARM C is performed for filling the cerebellar lobules in the final reconstructed volume with the proper aligned tissue.

# Citation
Piluso, S., Veraszto, C., Carey, H., Delattre, E., L’Yvonnet, T., Colnot, E., Romani, A., Bjaalie, J. G., Markram, H., & Keller, D. (2024). An extended and improved CCFv3 annotation and Nissl atlas of the entire mouse brain. bioRxiv, doi: 0.1101/2024.11.06.622212.

# Funding & Acknowledgment
The development of this software was supported by funding to the Blue Brain Project, a research center of the École polytechnique fédérale de Lausanne (EPFL), from the Swiss government's ETH Board of the Swiss Federal Institutes of Technology.
Copyright (c) 2024 Blue Brain Project/EPFL
