import numpy as np
import matplotlib.pyplot as plt
import csv
import nrrd



def extract_rgb_values(csv_file):
    color_data = {}
    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=':')
        for row in reader:
            label, rgb_str = row[0], row[1].strip()[1:-1]  # Extracting label and RGB string
            rgb_values = [int(val) for val in rgb_str.split(',')]  # Converting RGB string to list of integers
            color_data[int(label)] = rgb_values  # Storing label as integer and RGB values
    return color_data

def load_annotation_volume(annotation_file, color_file, points_file, incidence_file):
    # Load the NRRD annotation volume
    volume, header = nrrd.read(annotation_file)

    # Extract RGB values from the CSV color file
    color_data = extract_rgb_values(color_file)

    # Load the points from the NumPy file
    points = np.load(points_file)

    # Load the orientations from the NumPy file
    orientations = np.load(incidence_file)

    # Create a figure for coronal plots
    num_plots = len(points[0])
    num_cols = 5
    num_rows = (num_plots + num_cols - 1) // num_cols
    fig_coronal, axes_coronal = plt.subplots(num_rows, num_cols, figsize=(15, 15))
    fig_coronal.set_facecolor('black')

    # Plot each slice with colored labels and points for coronal incidence
    for i in range(num_plots):
        z, y, x = points[:, i]  # Coordinates are already in [z, y, x] order
        slice_img = volume[:, y, :]  # Extract the coronal slice corresponding to the current point
        slice_img = np.rot90(slice_img, k=3)
        slice_img = slice_img[:, ::-1]
        slice_img = slice_img[::-1, :]
        slice_rgb = np.zeros(slice_img.shape + (3,), dtype=np.uint8)  # Create an RGB image with the same dimensions as the slice
        for label, color in color_data.items():
            label_mask = (slice_img == label)
            slice_rgb[label_mask] = np.array(color)
        ax = axes_coronal[i // num_cols, i % num_cols]
        ax.imshow(slice_rgb)
        ax.scatter(z, volume.shape[2] - x, c='red', marker='o', label='Point')
        ax.text(0.02, 0.95, f'{i+1}', fontsize=8, color='white', transform=ax.transAxes, ha='left', va='top')
        ax.set_xticks([])
        ax.set_yticks([])
        # Set background color to black if a point is being plotted
        if len(ax.collections) > 0:
            ax.set_facecolor('black')

    # Hide empty subplots
    for i in range(num_plots, num_rows * num_cols):
        axes_coronal.flatten()[i].axis('off')

    plt.tight_layout()
    plt.show()

    # Create a figure for sagittal plots
    fig_sagittal, axes_sagittal = plt.subplots(num_rows, num_cols, figsize=(15, 15))
    fig_sagittal.set_facecolor('black')

    # Plot each slice with colored labels and points for sagittal incidence
    for i in range(num_plots):
        z, y, x = points[:, i]  # Coordinates are already in [z, y, x] order
        slice_img = volume[:, :, x]  # Extract the sagittal slice corresponding to the current point
        slice_img = np.rot90(slice_img, k=3)
        slice_img = slice_img[:, ::-1]
        slice_rgb = np.zeros(slice_img.shape + (3,), dtype=np.uint8)  # Create an RGB image with the same dimensions as the slice
        for label, color in color_data.items():
            label_mask = (slice_img == label)
            slice_rgb[label_mask] = np.array(color)
        ax = axes_sagittal[i // num_cols, i % num_cols]
        ax.imshow(slice_rgb)
        ax.scatter(z, y, c='red', marker='o', label='Point')  # Corrected coordinates for sagittal incidence
        ax.text(0.025, 0.95, f'{i+1}', fontsize=8, color='white', transform=ax.transAxes, ha='left', va='top')        
        ax.set_xticks([])
        ax.set_yticks([])
        # Set background color to black if a point is being plotted
        if len(ax.collections) > 0:
            ax.set_facecolor('black')

    # Hide empty subplots
    for i in range(num_plots, num_rows * num_cols):
        axes_sagittal.flatten()[i].axis('off')

    plt.tight_layout()
    plt.show()

    # Create a figure for axial plots
    fig_axial, axes_axial = plt.subplots(num_rows, num_cols, figsize=(15, 15))
    fig_axial.set_facecolor('black')

    # Plot each slice with colored labels and points for axial incidence
    for i in range(num_plots):
        z, y, x = points[:, i]
        slice_img = volume[z, :, :]  # Extract the axial slice corresponding to the current point
        slice_img = slice_img[:, ::-1]
        slice_rgb = np.zeros(slice_img.shape + (3,), dtype=np.uint8)  # Create an RGB image with the same dimensions as the slice
        for label, color in color_data.items():
            label_mask = (slice_img == label)
            slice_rgb[label_mask] = np.array(color)
        ax = axes_axial[i // num_cols, i % num_cols]
        ax.imshow(slice_rgb)
        ax.scatter(volume.shape[2] - x, y, c='red', marker='o', label='Point')
        ax.text(0.04, 0.95, f'{i+1}', fontsize=8, color='white', transform=ax.transAxes, ha='left', va='top')
        ax.set_xticks([])
        ax.set_yticks([])
        # Set background color to black if a point is being plotted
        if len(ax.collections) > 0:
            ax.set_facecolor('black')

    # Hide empty subplots
    for i in range(num_plots, num_rows * num_cols):
        axes_axial.flatten()[i].axis('off')

    plt.tight_layout()
    plt.show()

# Exexcution
annotation_file = '/home/piluso/data/10_ccfv2_TO_ccfv3/04_point_quality_evaluation/annotation_25_2022_CCFv3_0_hemir.nrrd'
color_file = '/home/piluso/data/00_allen_brain_atlas/region_rgb_colors.csv'
points_file = '/home/piluso/data/10_ccfv2_TO_ccfv3/04_point_quality_evaluation/coord/atlas_ref_coord.npy'
incidence_file = '/home/piluso/data/10_ccfv2_TO_ccfv3/04_point_quality_evaluation/coord/incidence.npy'
load_annotation_volume(annotation_file, color_file, points_file, incidence_file)
