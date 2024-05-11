"""
File: auto_label_images.py
Author: Dylan Turland Cowell
Date Created: 11-May-2024
Description: Using a pre trained model from tensor_hub, this script generates a bounding box file in 
'Edge Impulse Bounding Box Labelling' format, given the desired classes.
"""

import os
import tensorflow as tf
import tensorflow_hub as hub
import json

# Receive trained model
# module_handle = "https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1"              # Less accurate but fast
module_handle = "https://tfhub.dev/google/faster_rcnn/openimages_v4/inception_resnet_v2/1" # Accurate but slow
# Set trained model, 'detector' with default weightings (openimages classifications)
detector = hub.load(module_handle).signatures['default']

def load_img(path):
    """
    Load image from a specified path.
    Args:
        path (str): The path to the image file.
    Returns:
        Tensor: The loaded image.
    """
    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)
    return img

def run_detector(detector, path, wanted_classes, confidence):
    """
    Run object detection on an image to obtain class names, confidence and bounding box information of class instances in the image
    Args:
        detector: The loaded object detection model.
        path (str): The path to the image file.
        wanted_classes (list): List of class names to filter detections.
        confidence (float): Minimum confidence threshold for detections.
    Returns:
        classes (list): List of class names and a list of bounding boxes.
        bb (list): List of bounding box data in TF format.
    """
    img = load_img(path)
    converted_img = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]
    result = detector(converted_img)
    result = {key: value.numpy() for key, value in result.items()}
    
    # Obtain filtered detections
    bb, classes, scores = filter_detections(result["detection_boxes"], result["detection_class_entities"], result["detection_scores"], wanted_classes, confidence) 
    
    return classes, bb

def filter_detections(bb, class_name, score, desired_classes, confidence):
    """
    Filter detections based on class names and confidence, allowing customisable returns.
    Args:
        bb (list): List of bounding boxes.
        class_name (list): List of class names.
        score (list): List of detection scores.
        desired_classes (list): List of class names to filter detections.
        confidence (float): Minimum confidence threshold for detections.
    Returns:
        filtered_boxes (list): Nested lists of filtered bounding boxes.
        filtered_classes (list): Nested lists of class names.
        filtered_scores (list): Nested lists of scores.
    """    
    
    filtered_boxes = []
    filtered_classes = []
    filtered_scores = []
    
    for i in range(len(score)):
        if class_name[i].decode("utf-8") in desired_classes:
            if score[i] > confidence:
                filtered_boxes.append(bb[i].tolist())  # Convert array to list
                filtered_classes.append(class_name[i].decode("utf-8"))
                filtered_scores.append(score[i])
                
    return filtered_boxes, filtered_classes, filtered_scores

def process_images_in_directory(directory_path, wanted_classes, minimum_confidence):
    """
    Execute model detection on all images in a directory
    Args:
        directory_path (str): The path to the directory containing images.
        wanted_classes (list): List of class names to filter detections.
        minimum_confidence (float): Minimum confidence threshold for detections.
    Returns:
        tuple: A tuple containing lists of image names, class names, and bounding boxes.
    """
    
    all_image_names = []
    all_class_names = []
    all_bounding_boxes = []
    
    # Iterate through each file in the directory
    for filename in os.listdir(directory_path):
        if filename.lower().endswith('.jpg'): # Ensure jpg
            image_path = os.path.join(directory_path, filename)
            classes, bounding_boxes = run_detector(detector, image_path, wanted_classes, minimum_confidence)
            
            # Add data to lists
            all_image_names.append(filename)
            all_class_names.append(classes)
            all_bounding_boxes.append(bounding_boxes)
    
    return all_image_names, all_class_names, all_bounding_boxes


def save_bounding_box_data(image_names, class_names_list, bounding_boxes_list, img_height=426, img_width=640):
    """
    Interpret TF model output and translate to Edge Impulse Object Detection Labelling (EI format) format and saves the file.
    Args:
        image_names (list): List of image names.
        class_names_list (list): List of lists of class names.
        bounding_boxes_list (list): List of lists of bounding boxes.
        img_height (int): Height of the images.
        img_width (int): Width of the images.
    """
   
    # Header of EI format
    data = {
        "version": 1,
        "type": "bounding-box-labels",
        "boundingBoxes": {}
    }
    
    # Iterate through each image's name, classes and bounding boxes
    for image_name, class_names, bounding_boxes in zip(image_names, class_names_list, bounding_boxes_list):
        # For each image, get the new bounding box data
        data["boundingBoxes"][image_name] = []
        for label, box in zip(class_names, bounding_boxes):
            ymin, xmin, ymax, xmax = box
            height = int((ymax - ymin) * img_height)
            width = int((xmax - xmin) * img_width)
            x = int(xmin * img_width)
            y = int(ymin * img_height)

            # Append new data
            data["boundingBoxes"][image_name].append({
                "label": label,
                "x": x,
                "y": y,
                "width": width,
                "height": height
            })

        # After generating all labelling data, save to file
        with open('Generated_file_location', 'w') as file:
            json.dump(data, file, indent=4)


# Define the directory containing images
image_directory = "Image_directory"

# Define parameters
wanted_classes = ['Dog', 'Pillow'] # Example list of classes to define - ensure compatible with pre-trained model dataset (e.g. Coco has 80 classes and faster_rcnn has 600)
minimum_confidence = 0.7

# Process images in the directory
image_names, all_classes, all_bounding_boxes = process_images_in_directory(image_directory, wanted_classes, minimum_confidence)

save_bounding_box_data(image_names, all_classes, all_bounding_boxes)
