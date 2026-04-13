# 01 Python Data Processing

## Overview
This section demonstrates my Python-based data processing work for a face recognition preprocessing pipeline. The script automates image resizing, file renaming, folder organization, eye-coordinate extraction, unmatched sample separation, and output verification before later training or evaluation stages.

## Input
The preprocessing pipeline accepts:
- a raw image dataset directory
- a coordinate output directory
- an unmatched output directory

Example:
- `testing_dataset/`
- `testing_dataset_coord/`
- `testing_dataset_unmatch/`

## Processing Workflow
The script performs the following steps:

1. Reads raw face images from the input directory.
2. Resizes all images to `1024x1024` if they are not already in that format.
3. Renames each image using a five-digit format such as `00000`, `00001`, etc.
4. Places each renamed image into its own uniquely named folder.
5. Detects left and right eye coordinates using MediaPipe Face Mesh.
6. Saves the detected eye coordinates as metadata text files in the coordinate directory.
7. Moves images for which eye coordinates cannot be detected into a separate unmatched directory.
8. Renames the remaining image folders and files sequentially after unmatched samples are removed.
9. Verifies consistency between processed image folders and coordinate folders.

## Output
The preprocessing pipeline produces three outputs:

- **Processed image directory**  
  Renamed images organized into unique folders.

- **Coordinate metadata directory**  
  Eye-coordinate metadata stored in per-image folders.

- **Unmatched directory**  
  Images for which valid eye coordinates could not be detected.

Example output structure:
- `testing_dataset/00000/00000.png`
- `testing_dataset_coord/meta/00000/00000.txt`
- `testing_dataset_unmatch/`

## Main Script
- `preprocess.py`

## How to Run
```bash
python preprocess.py --data_dir testing_dataset --coord_dir testing_dataset_coord --unmatched_dir testing_dataset_unmatch
