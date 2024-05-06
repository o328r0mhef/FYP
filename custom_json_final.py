import json
from pycocotools.coco import COCO

def generate_filtered_json(input_json_file, output_json_file, classes):
    # Load the COCO JSON file
    coco = COCO(input_json_file)

    # Get the category IDs for the specified classes
    category_ids = coco.getCatIds(catNms=classes)

    # Get all annotations for the specified classes
    filtered_annotations = []
    for cat_id in category_ids:
        annotations = coco.loadAnns(coco.getAnnIds(catIds=[cat_id]))
        for ann in annotations:
            # Check if the annotation belongs to the specified class
            if ann['category_id'] == cat_id:
                filtered_annotations.append(ann)

    # Collect unique image IDs associated with the filtered annotations
    image_ids = set([ann['image_id'] for ann in filtered_annotations])

    # Retrieve image information for the unique image IDs
    images = [coco.imgs[image_id] for image_id in image_ids]

    # Create a new COCO dataset with only the specified annotations
    filtered_coco = {
        "info": coco.dataset["info"],
        "licenses": coco.dataset["licenses"],
        "images": images,
        "annotations": filtered_annotations,
        "categories": [coco.cats[cat_id] for cat_id in category_ids]
    }

    # Save the filtered annotations to a new JSON file
    with open(output_json_file, 'w') as f:
        json.dump(filtered_coco, f)

    print("Filtered annotations saved to", output_json_file)

# Example usage
input_json_file = "C:/Users/Dylan/fiftyone/coco-2017/raw/instances_train2017.json"
output_json_file = 'C:/Users/Dylan/FYP - ML Code Local/five_training_labels.json'
classes = classes=["dog", "car", "bench", "person", "chair"]  # List of classes you want to include
generate_filtered_json(input_json_file, output_json_file, classes)
