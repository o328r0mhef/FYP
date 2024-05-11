auto_label_images.py

Author: Dylan Turland Cowell

Date Created: 11-May-2024

Description: Using a pre-trained model from TensorFlow Hub, this script generates a bounding box file in 'Edge Impulse Bounding Box Labelling' format, given the desired classes.
Script Overview

This script utilizes a pre-trained object detection model from TensorFlow Hub to generate bounding box annotations for images. It processes images in a specified directory, detects objects within them, and saves the resulting bounding box data in a format compatible with Edge Impulse.
Functionality
load_img(path)

Load an image from a specified path.
run_detector(detector, path, wanted_classes, confidence)

Run object detection on an image to obtain class names, confidence scores, and bounding box information.
filter_detections(bb, class_name, score, desired_classes, confidence)

Filter detections based on class names and confidence scores.
process_images_in_directory(directory_path, wanted_classes, minimum_confidence)

Execute model detection on all images in a directory.
save_bounding_box_data(image_names, class_names_list, bounding_boxes_list, img_height=426, img_width=640)

Interpret TF model output and translate it to Edge Impulse Object Detection Labelling format and save the file.
Usage

    Set the parameters such as the image directory, desired classes, and minimum confidence threshold.
    Run the script.
