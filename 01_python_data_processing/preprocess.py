import os
import shutil
import cv2
import mediapipe as mp
from tqdm import tqdm
from PIL import Image
import argparse

def resize1024x1024(directory):
    # Get the list of image files
    file_list = [file_name for file_name in os.listdir(directory) if file_name.endswith((".jpg", ".png"))]

    # Check if all images are already 1024x1024
    all_1024 = True
    for file_name in file_list:
        img_path = os.path.join(directory, file_name)
        with Image.open(img_path) as img:
            if img.size != (1024, 1024):
                all_1024 = False
                break  # No need to check further

    if all_1024:
        print("All images are already 1024x1024. Skipping resizing process.")
        return

    # Process images with a progress bar
    for file_name in tqdm(file_list, desc="Resizing Images to 1024x1024", unit="image"):
        img_path = os.path.join(directory, file_name)
        with Image.open(img_path) as img:
            if img.size == (1024, 1024):
                continue  # Skip already resized images
            
            img = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)
            img.save(img_path)

    print("Resizing process completed.")

# Initialize MediaPipe Face Mesh for detecting eye coordinates
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)

def rename_folders_and_files(directory):
    """Rename all image files and move them into uniquely named folders."""
    files = sorted([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
    
    with tqdm(total=len(files), desc="Renaming images and organizing folders", unit="file") as pbar:
        for idx, file in enumerate(files):
            old_file_path = os.path.join(directory, file)
            new_folder_name = f"{idx:05d}"
            new_folder_path = os.path.join(directory, new_folder_name)
            os.makedirs(new_folder_path, exist_ok=True)
            
            new_file_name = f"{new_folder_name}{os.path.splitext(file)[1]}"
            new_file_path = os.path.join(new_folder_path, new_file_name)
            os.rename(old_file_path, new_file_path)
            pbar.update(1)

def detect_eye_coordinates(image_path):
    """
    Detects left and right eye coordinates using MediaPipe.
    """
    image = cv2.imread(image_path)
    if image is None:
        return None

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_image)
    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0]
        width, height = image.shape[1], image.shape[0]
        
        left_eye_center = (
            int(face_landmarks.landmark[468].x * width),
            int(face_landmarks.landmark[468].y * height)
        )
        right_eye_center = (
            int(face_landmarks.landmark[473].x * width),
            int(face_landmarks.landmark[473].y * height)
        )
        return [left_eye_center, right_eye_center]
    return None

def save_eye_coordinates(meta_folder, image_name, eye_coordinates):
    """
    Saves detected eye coordinates into a folder inside meta, each with its own name.
    """
    coord_folder = os.path.join(meta_folder, image_name)
    os.makedirs(coord_folder, exist_ok=True)
    txt_path = os.path.join(coord_folder, f"{image_name}.txt")
    with open(txt_path, 'w') as f:
        f.write(f"Left Eye: {eye_coordinates[0]}\n")
        f.write(f"Right Eye: {eye_coordinates[1]}\n")

def process_directory(input_directory, output_directory):
    """
    Processes images in the directory, detects eye coordinates, and saves them.
    """
    meta_dir = os.path.join(output_directory, "meta")
    os.makedirs(meta_dir, exist_ok=True)
    
    image_folders = [d for d in os.listdir(input_directory) if os.path.isdir(os.path.join(input_directory, d))]
    with tqdm(total=len(image_folders), desc="Processing Images", unit="folder") as pbar:
        for folder in image_folders:
            image_files = [f for f in os.listdir(os.path.join(input_directory, folder)) if f.endswith(('.png', '.jpg', '.jpeg'))]
            if not image_files:
                pbar.update(1)
                continue
            
            image_path = os.path.join(input_directory, folder, image_files[0])
            eye_coordinates = detect_eye_coordinates(image_path)
            if eye_coordinates:
                save_eye_coordinates(meta_dir, folder, eye_coordinates)
            pbar.update(1)

def move_and_rename_folders(image_directory, coordinate_directory, destination_directory):
    """Move folders without corresponding coordinates, rename remaining folders and their files properly."""
    os.makedirs(destination_directory, exist_ok=True)

    image_folders = sorted([
        folder for folder in os.listdir(image_directory)
        if folder.isdigit() and os.path.isdir(os.path.join(image_directory, folder))
    ], key=int)

    # Move folders without coordinate files
    folders_to_move = [
        folder for folder in image_folders
        if not os.path.exists(os.path.join(coordinate_directory, "meta", folder, f"{folder}.txt"))
    ]
    
    for folder in folders_to_move:
        shutil.move(os.path.join(image_directory, folder), os.path.join(destination_directory, folder))
        print(f"Moved: {folder} to {destination_directory}")

    # Rename remaining folders in sequential order
    remaining_folders = sorted([
        folder for folder in os.listdir(image_directory)
        if folder.isdigit() and os.path.isdir(os.path.join(image_directory, folder))
    ], key=int)

    folder_rename_map = {}
    for new_index, old_folder in enumerate(remaining_folders):
        new_folder_name = f"{new_index:05d}"
        if old_folder != new_folder_name:
            os.rename(os.path.join(image_directory, old_folder), os.path.join(image_directory, new_folder_name))
            folder_rename_map[old_folder] = new_folder_name
            print(f"Renamed folder: {old_folder} -> {new_folder_name}")

    # Rename images and coordinate files accordingly
    for old_folder, new_folder in folder_rename_map.items():
        new_folder_path = os.path.join(image_directory, new_folder)

        for ext in ['.jpg', '.png']:
            old_image_path = os.path.join(new_folder_path, f"{old_folder}{ext}")
            new_image_path = os.path.join(new_folder_path, f"{new_folder}{ext}")

            if os.path.exists(old_image_path):
                os.rename(old_image_path, new_image_path)
                print(f"Renamed image: {old_image_path} -> {new_image_path}")

    for old_folder, new_folder in folder_rename_map.items():
        old_coordinate_folder = os.path.join(coordinate_directory, "meta", old_folder)
        new_coordinate_folder = os.path.join(coordinate_directory, "meta", new_folder)
        old_coordinate_file = os.path.join(old_coordinate_folder, f"{old_folder}.txt")
        new_coordinate_file = os.path.join(new_coordinate_folder, f"{new_folder}.txt")

        if os.path.exists(old_coordinate_file):
            os.makedirs(new_coordinate_folder, exist_ok=True)
            shutil.move(old_coordinate_file, new_coordinate_file)
            print(f"Renamed coordinate file: {old_coordinate_file} -> {new_coordinate_file}")

            if not os.listdir(old_coordinate_folder):
                os.rmdir(old_coordinate_folder)

def count_and_check_files_recursive(image_root_dir, coord_root_dir):
    """Compares image and coordinate files to check for missing files."""
    image_folders = set(os.listdir(image_root_dir))
    coord_folders = set(os.listdir(os.path.join(coord_root_dir, "meta")))
    
    missing_coords = image_folders - coord_folders
    missing_images = coord_folders - image_folders
    
    print(f"Total Image Folders: {len(image_folders)}")
    print(f"Total Coordinate Folders: {len(coord_folders)}")
    
    if missing_coords:
        print("\nMissing Coordinate Folders:")
        for name in sorted(missing_coords):
            print(f"  {name}")
    
    if missing_images:
        print("\nMissing Image Folders:")
        for name in sorted(missing_images):
            print(f"  {name}")
    
    if not missing_coords and not missing_images:
        print("\nAll files are matched correctly!")

if __name__ == "__main__":
     
    parser = argparse.ArgumentParser(description="Full preprocessing pipeline")
    parser.add_argument("--data_dir", type=str, required=True, help="Raw image directory")
    parser.add_argument("--coord_dir", type=str, required=True, help="Coordinate output directory")
    parser.add_argument("--unmatched_dir", type=str, required=True, help="Unmatched output directory")

    args = parser.parse_args()
    dataset_directory = args.data_dir
    dataset_coordinate_directory = args.coord_dir
    unmatched_directory = args.unmatched_dir
    print(f"Starting pipeline with directories:\n  Data: {dataset_directory}\n  Coord: {dataset_coordinate_directory}\n  Unmatched: {unmatched_directory}\n")
    
    resize1024x1024(dataset_directory)
    print("Image resizing completed.")

    rename_folders_and_files(dataset_directory)
    print("Renaming and organizing completed.")

    process_directory(dataset_directory, dataset_coordinate_directory)
    print("Coordinate processing completed.")

    move_and_rename_folders(dataset_directory, dataset_coordinate_directory, unmatched_directory)
    print("Folder cleanup and renaming completed.")

    count_and_check_files_recursive(dataset_directory, dataset_coordinate_directory)
    print("Coordinate verification completed.")
