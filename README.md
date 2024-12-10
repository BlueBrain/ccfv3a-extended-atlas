# ccfv3a-extended-atlas

# Overview
This repository contains the code developed for producing the CCFv3aBBP Nissl-based atlas, an extension of the Allen Institute's Common Coordinate Framework version 3 (CCFv3).
The project focuses on enhancing the anatomical correspondance between the Allen Reference Atlas (ARA) Nissl stained volume and the CCFv3 annotations and integrate the necessary data (anatomiy and annotation) to provide a comprehensive atlas of the entire mouse brain.
This new atlas version extends the main olfactory bulb, cerebellum, and medulla regions. Some additional layers are also incorporated within the resulting CCFv3cBBP version, such as the barrel columns and the spinal cord.
This project also made it possible to produce an average Nissl template based on 734 mouse brains.
The pipelines provided in that code gathers several alignement-based methods for performing a region-based registration mainly, divided into 3 Automated Registration Methods (ARM):
- ARM A: Alignement of the ARA Nissl volume in the CCFv3,
- ARM B: Extension of the main olfactory bulb,
- ARM C: Extension of the cerebellum/medulla.

![Capture d’écran du 2024-12-10 15-29-53](https://github.com/user-attachments/assets/15d9a75e-ccf6-43d6-9da8-c69b0e10bd43)

# Features
1. Mask the data: `mask_id_annot_whole_vol_with_descendants.py`
2. Register the data: `CCFv2_to_CCFv3_registration_niftireg_pipeline.py`

# Installation
```
git clone https://github.com/BlueBrain/ccfv3a-extended-atlas.git
cd CCFv3aBBP  
pip install -r requirements.txt 
```

# Citation
Piluso, S., Veraszto, C., Carey, H., Delattre, E., L’Yvonnet, T., Colnot, E., Romani, A., Bjaalie, J. G., Markram, H., & Keller, D. (2024). An extended and improved CCFv3 annotation and Nissl atlas of the entire mouse brain. bioRxiv, doi: 0.1101/2024.11.06.622212.

# Funding & Acknowledgment
The development of this software was supported by funding to the Blue Brain Project, a research center of the École polytechnique fédérale de Lausanne (EPFL), from the Swiss government's ETH Board of the Swiss Federal Institutes of Technology.
Copyright (c) 2024 Blue Brain Project/EPFL
