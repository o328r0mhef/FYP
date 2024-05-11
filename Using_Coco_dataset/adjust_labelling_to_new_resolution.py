import json

def adjust_bbox(bbox, scale_factor):
    # Adjust bounding box coordinates
    adjusted_bbox = [
        int(coord / scale_factor) for coord in bbox
    ]
    return adjusted_bbox

def resize_annotations(json_file, scale_factor):
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Loop through each annotation
    for annotation in data['annotations']:
        # Adjust bounding box coordinates
        bbox = annotation['bbox']
        adjusted_bbox = adjust_bbox(bbox, scale_factor)
        annotation['bbox'] = adjusted_bbox

    # Save the modified JSON file
    with open('C:/Users/Dylan/fiftyone/coco-2017_75000/train/data_240_max/bounding_boxes.json', 'w') as f:
        json.dump(data, f, indent=4)

# Adjusted scale factor based on image resizing (original_resolution / new_resolution)
scale_factor = 640 / 240  # Example: 640 pixels to 96 pixels

# Provide the path to your original JSON file containing bounding box annotations
original_json_file = 'C:/Users/Dylan/fiftyone/coco-2017_75000/train/bounding_boxes_original.json'

# Resize the bounding box annotations and save the modified JSON file
resize_annotations(original_json_file, scale_factor)
