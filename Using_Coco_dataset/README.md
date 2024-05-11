Scripts
1. custom_json_labelling.py

    Description: This script should be used with the fiftyone library. After downloading the desired amount of images and classes, it generates a new labelling file compatible with Edge Impulse. Fiftyone attempts this, but the labelling file output is not directly compatible with Edge Impulse.

    Dependencies:
        json,
        pycocotools

2. change_resolution.py

    Description: This script iterates through a directory of downloaded images to reduce their peak axis resolution (640 from Coco 2017 dataset) to a new defined resolution.

    Dependencies:
        os,
        PIL

3. adjust_labelling_to_new_resolution.py

    Description: This script iterates through the labelling file generated from custom_json_labelling.py and adjusts the sizes of the bounding boxes. This enables annotations for the resized images generated from the change_resolution.py script.

    Dependencies:
        json
