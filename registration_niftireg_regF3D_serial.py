import os
import sys
from nipype.interfaces import niftyreg


ref_folder = os.path.abspath(sys.argv[1])
flo_folder = os.path.abspath(sys.argv[2])
ouptut_folder = os.path.abspath(sys.argv[3])

ref_file_list = [f for f in os.listdir(ref_folder) if f.endswith(".nii")]
flo_file_list = [f for f in os.listdir(flo_folder) if f.endswith(".nii")]

ref_file_path = [os.path.join(ref_folder,f) for f in ref_file_list]
flo_file_path = [os.path.join(flo_folder,f) for f in flo_file_list]

nb_files = len(ref_file_list)
nb_files2 = len(flo_file_list)

if nb_files != nb_files2:
        print("ERROR: not the same numer of files compared")
        sys.exit(1)
else:
    for i in range(nb_files):
        ref_file = ref_file_path[i]
        flo_file =  flo_file_path[i]
        if ref_file_list[i] == flo_file_list[i]:
            output_file_path = os.path.join(ouptut_folder, ref_file_list[i].split(".nii")[0] + "_res.nii.gz")

            node = niftyreg.RegF3D()
            node.inputs.ref_file = ref_file
            node.inputs.flo_file = flo_file
            ouptut_res_file_path = output_file_path

            node.inputs.res_file = ouptut_res_file_path
            output_cpp_file_path = ouptut_res_file_path.replace("_res.nii.gz", "_cpp.nii.gz")
            node.inputs.cpp_file = output_cpp_file_path
            # node.inputs.rmask_file = 'mask.nii'
            # node.inputs.omp_core_val = 4
            print(node.cmdline)
            node.run()
        else:
            print("ERROR: not the same files being compared: " + ref_file_list[i] + " TO " + flo_file_list[i])
            sys.exit(1)


"""
INPUT
[Mandatory]
flo_file: (an existing file name)
        The input floating/source image
        flag: -flo %s
ref_file: (an existing file name)
        The input reference/target image
        flag: -ref %s

[Optional]
aff_file: (an existing file name)
        The input affine transformation file
        flag: -aff %s
amc_flag: (a boolean)
        Use additive NMI
        flag: -amc
args: (a unicode string)
        Additional parameters to the command
        flag: %s
be_val: (a float)
        Bending energy value
        flag: -be %f
cpp_file: (a file name)
        The output CPP file
        flag: -cpp %s
environ: (a dictionary with keys which are a bytes or None or a value
         of class 'str' and with values which are a bytes or None or a value
         of class 'str', nipype default value: {})
        Environment variables
fbn2_val: (a tuple of the form: (a long integer >= 0, a long integer
         >= 0))
        Number of bins in the histogram for reference image for given time
        point
        flag: -fbn %d %d
fbn_val: (a long integer >= 0)
        Number of bins in the histogram for reference image
        flag: --fbn %d
flo_smooth_val: (a float)
        Smoothing kernel width for floating image
        flag: -smooF %f
flwth2_thr_val: (a tuple of the form: (a long integer >= 0, a float))
        Lower threshold for floating image at the specified time point
        flag: -fLwTh %d %f
flwth_thr_val: (a float)
        Lower threshold for floating image
        flag: --fLwTh %f
fmask_file: (an existing file name)
        Floating image mask
        flag: -fmask %s
fupth2_thr_val: (a tuple of the form: (a long integer >= 0, a float))
        Upper threshold for floating image at the specified time point
        flag: -fUpTh %d %f
fupth_thr_val: (a float)
        Upper threshold for floating image
        flag: --fUpTh %f
incpp_file: (an existing file name)
        The input cpp transformation file
        flag: -incpp %s
jl_val: (a float)
        Log of jacobian of deformation penalty value
        flag: -jl %f
kld2_flag: (a long integer >= 0)
        Use KL divergence as the similarity measure for a given time point
        flag: -kld %d
kld_flag: (a boolean)
        Use KL divergence as the similarity measure
        flag: --kld
le_val: (a float)
        Linear elasticity penalty term
        flag: -le %f
ln_val: (a long integer >= 0)
        Number of resolution levels to create
        flag: -ln %d
lncc2_val: (a tuple of the form: (a long integer >= 0, a float))
        SD of the Gaussian for computing LNCC for a given time point
        flag: -lncc %d %f
lncc_val: (a float)
        SD of the Gaussian for computing LNCC
        flag: --lncc %f
lp_val: (a long integer >= 0)
        Number of resolution levels to perform
        flag: -lp %d
maxit_val: (a long integer >= 0)
        Maximum number of iterations per level
        flag: -maxit %d
nmi_flag: (a boolean)
        use NMI even when other options are specified
        flag: --nmi
no_app_jl_flag: (a boolean)
        Do not approximate the log of jacobian penalty at control points
        only
        flag: -noAppJL
noconj_flag: (a boolean)
        Use simple GD optimization
        flag: -noConj
nopy_flag: (a boolean)
        Do not use the multiresolution approach
        flag: -nopy
nox_flag: (a boolean)
        Don't optimise in x direction
        flag: -nox
noy_flag: (a boolean)
        Don't optimise in y direction
        flag: -noy
noz_flag: (a boolean)
        Don't optimise in z direction
        flag: -noz
omp_core_val: (an integer (int or long), nipype default value: 1)
        Number of openmp thread to use
        flag: -omp %i
pad_val: (a float)
        Padding value
        flag: -pad %f
pert_val: (a long integer >= 0)
        Add perturbation steps after each optimization step
        flag: -pert %d
rbn2_val: (a tuple of the form: (a long integer >= 0, a long integer
         >= 0))
        Number of bins in the histogram for reference image for given time
        point
        flag: -rbn %d %d
rbn_val: (a long integer >= 0)
        Number of bins in the histogram for reference image
        flag: --rbn %d
ref_smooth_val: (a float)
        Smoothing kernel width for reference image
        flag: -smooR %f
res_file: (a file name)
        The output resampled image
        flag: -res %s
rlwth2_thr_val: (a tuple of the form: (a long integer >= 0, a float))
        Lower threshold for reference image at the specified time point
        flag: -rLwTh %d %f
rlwth_thr_val: (a float)
        Lower threshold for reference image
        flag: --rLwTh %f
rmask_file: (an existing file name)
        Reference image mask
        flag: -rmask %s
rupth2_thr_val: (a tuple of the form: (a long integer >= 0, a float))
        Upper threshold for reference image at the specified time point
        flag: -rUpTh %d %f
rupth_thr_val: (a float)
        Upper threshold for reference image
        flag: --rUpTh %f
smooth_grad_val: (a float)
        Kernel width for smoothing the metric gradient
        flag: -smoothGrad %f
ssd2_flag: (a long integer >= 0)
        Use SSD as the similarity measure for a given time point
        flag: -ssd %d
ssd_flag: (a boolean)
        Use SSD as the similarity measure
        flag: --ssd
sx_val: (a float)
        Final grid spacing along the x axes
        flag: -sx %f
sy_val: (a float)
        Final grid spacing along the y axes
        flag: -sy %f
sz_val: (a float)
        Final grid spacing along the z axes
        flag: -sz %f
vel_flag: (a boolean)
        Use velocity field integration
        flag: -vel
verbosity_off_flag: (a boolean)
        Turn off verbose output
        flag: -voff

OUTPUT
avg_output: (a string)
        Output string in the format for reg_average
cpp_file: (a file name)
        The output CPP file
invcpp_file: (a file name)
        The output inverse CPP file
invres_file: (a file name)
        The output inverse res file
res_file: (a file name)
        The output resampled image
"""
