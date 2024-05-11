These three scripts can be used with the ''fiftyone' library to manipulate the Coco dataset.

'custom_json_labelling' should be used with the fiftyone library. After downloading the desired amount of images and classes, this script generates a new labelling file to be used with the data. Fiftyone attempts this but the labelling file output is not compatible with Edge Impulse.

'change_resolution' iterates through a directory of downloaded images to reduce the resolution. 
                    Dependencies: os, PIL

'custom_json_labelling' iterates through the labelling file generated from 'custom_json_labelling' and adjusts the sizes of the bounding boxes. This enables annotations for the resized images generated from the 'change_resolution' script.
