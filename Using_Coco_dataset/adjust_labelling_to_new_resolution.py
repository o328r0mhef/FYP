"""
File: adjust_labelling_to_new_resolution.py
Author: Dylan Turland Cowell
Date Created: 11-May-2024
Description: This script is designed to be used with the 'resize_images.py' and 'custom_json_labelling.py' scripts.
             After reducing Coco dataset image resolutions and generating a custom labelling file, running this script adjusts the bounding boxes 
             to fit to the new resolution.
"""

import json

def adjust_bbox(bbox, scale_factor):
     """
    Adjust bounding box coordinates by dividing each coordinate by the scale_factor.

    Parameters:
    - bbox (list): List containing [x_min, y_min, width, height] of the bounding box.
    - scale_factor (float): Factor by which to scale down the bounding box coordinates.

    Returns:
    - adjusted_bbox (list): List containing adjusted [x_min, y_min, width, height].
    """
    adjusted_bbox = [
        int(coord / scale_factor) for coord in bbox
    ]
    return adjusted_bbox

def resize_annotations(json_file, scale_factor):
    """
    Resize annotations in a .json file by adjusting Coco bounding box coordinates.

    Parameters:
    - json_file (str): Path to the .json file containing annotations.
    - scale_factor (float): Factor by which to scale down the bounding box coordinates.
    """
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Loop through each annotation
    for annotation in data['annotations']:
        # Adjust bounding box coordinates
        bbox = annotation['bbox']
        adjusted_bbox = adjust_bbox(bbox, scale_factor)
        annotation['bbox'] = adjusted_bbox

    # Save the modified JSON file
    with open('new_directory/bounding_boxes.json', 'w') as f:
        json.dump(data, f, indent=4)

# Adjusted scale factor from image resising (original_resolution / new_resolution)
scale_factor = 640 / 240  # Example: 640 pixels to 240 pixels

# Path to your original .json file containing Coco bounding box labelling
original_json_file = 'directory_of_labelling_file_to_edit'

# Resize the bounding box annotations and save the modified JSON file
resize_annotations(original_json_file, scale_factor)
