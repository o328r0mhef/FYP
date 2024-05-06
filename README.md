Object Detection and Labelling using TensorFlow

This Python script uses TensorFlow and TensorFlow Hub to perform object detection on images and generate bounding box labels compatible with Edge Impulse Object Detection Labelling format for autolabelling.
Prerequisites:

    Python 3.8 - 3.12
    TensorFlow
    TensorFlow Hub

Install the required packages using pip:

pip install tensorflow tensorflow-hub

Usage:

    Load the pre-trained object detection model using TensorFlow Hub.
    Define helper functions to load images, run the detector, filter detections based on specified classes and confidence threshold, and process images in a directory.
    Execute model detection on all images in a specified directory.
    Translate the model output to Edge Impulse Object Detection Labelling format and save the bounding box data to a file.

To use the script:

    Set the image_directory variable to the path containing the images.
    Define the wanted_classes list with the desired classes to filter detections.
    Specify the minimum_confidence threshold for detections. Test with a small sample of images.    
    Run the script.

The script will process the images in the specified directory, perform object detection, generate bounding box labels, and save the data to a file named bounding_boxes.labels.
Customisation:

    Modify the wanted_classes list to include or exclude specific classes for detection.
    Adjust the minimum_confidence threshold to filter detections based on confidence scores.
