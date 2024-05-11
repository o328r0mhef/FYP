import os
from PIL import Image

# Function to resize images in a directory
def resize_images(input_dir, output_dir):
"""
Resize images in a directory while preserving aspect ratio and save them to another directory.

Parameters:
- input_dir (str): Path to the directory containing the original images.
- output_dir (str): Path to the directory where resized images will be saved.
"""
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Iterate through all files in the input directory
    for filename in os.listdir(input_dir):
        # Check if the file is an image
        if filename.endswith((".jpg", ".png")):
            # Open the image
            img = Image.open(os.path.join(input_dir, filename))

            # Calculate the new dimensions while preserving aspect ratio of bounding boxes
            width, height = img.size
            max_dimension = 240
            if width > height:
                new_width = max_dimension
                new_height = int(height * max_dimension / width)
            else:
                new_height = max_dimension
                new_width = int(width * max_dimension / height)

            # Resize the image
            img = img.resize((new_width, new_height))

            # Save the resized image to the output directory
            output_path = os.path.join(output_dir, filename)
            img.save(output_path)
# Set the input and output directories
input_directory = "original_image_directory"
output_directory = "new_image_directory"

# Resize images
resize_images(input_directory, output_directory)
