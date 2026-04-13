# 02 Linux Environment Setup

## Overview
This section demonstrates my ability to set up and manage a Linux-based development environment for a face recognition research project. The project is based on a prior benchmark implementation, and I configured the environment, installed dependencies, and adapted the setup so that the modified workflow could run correctly on Linux.

## Base Project
This environment setup is based on the benchmark implementation from the following paper:

**Vulnerability of State-of-the-Art Face Recognition Models to Template Inversion Attack**  
Hatef Otroshi Shahreza, Vedrana Krivokuća Hahn, Sébastien Marcel  
IEEE Transactions on Information Forensics and Security, 2024

The original benchmark provided the initial installation and experiment workflow. My work focused on preparing a functional Linux execution environment and extending it with additional dependencies needed for my modified project.

## Operating Environment
- Operating System: Ubuntu Linux
- Environment Manager: Conda
- Shell: Bash
- Main Language: Python

## Original Setup Procedure
The original benchmark project was installed on Linux using conda. The base setup process included:

```bash
cd bob.paper.tifs2024_face_ti
conda create --name bob.paper.tifs2024_face_ti --file package-list.txt
conda activate bob.paper.tifs2024_face_ti
buildout
```

## Additional Libraries Installed for the Modified Workflow
The original environment alone was not sufficient for my modified face recognition workflow. I additionally installed the following libraries to support preprocessing, model execution, and related tasks:

```bash
pip install timm six mkl-service alive-progress h5py
pip install --no-cache-dir mkl-service

pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install opencv-python gfpgan basicsr realesrgan facexlib
pip install pillow tqdm alive-progress
pip install mediapipe==0.10.21

pip install numpy==1.24.4 opencv-python opencv-contrib-python scipy scikit-image pyyaml
```

## Execution Workflow
After environment preparation, the project workflow was run on Linux using shell-based commands and scripts for preprocessing, training, and evaluation.

Example stages include:

- dataset preprocessing
- model training
- model evaluation

## My Contribution
Although this project was originally based on a prior benchmark implementation, my work extended it beyond simple reproduction. I followed the original Linux installation procedure as a starting point, but I additionally prepared the environment required for my own modified workflow by resolving dependency issues and installing extra libraries that were not sufficiently covered by the original setup.

Beyond environment preparation, I adapted the project to fit my research objectives. This included modifying the dataset configuration, adjusting the execution flow, changing training-related settings such as the learning rate, decay rate, and loss weighting, and refining the face-processing pipeline. In particular, I addressed practical issues related to facial alignment, since many training images did not contain perfectly upright faces and often showed slight left or right rotation. To address this issue, I modified the cropping mechanism used in the original Bob-based workflow so that the preprocessing stage could better handle slight facial rotations and alignment inconsistencies.

Overall, this work represents an improved research implementation built on top of the original benchmark, with substantial adaptation in the environment, preprocessing, and experimental workflow to support my own face recognition and reconstruction study.