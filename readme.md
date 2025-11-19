# IdentifyYou – Face Search Tool

## Overview

IdentifyYou is a desktop tool that scans a folder of images and identifies all photos containing a specific person's face. Users provide a folder of reference images, a folder of target images, and an optional output folder. The application detects faces, extracts embeddings using InsightFace, computes cosine similarity against the reference embeddings, and copies matched images to the destination folder.

This version includes a graphical interface built with Tkinter and uses a multithreaded execution model to speed up image processing on CPU. InsightFace's `buffalo_l` model is used for both face detection and feature extraction, and the application is packaged as a standalone executable using PyInstaller (no Python installation required for end users).

---

## Current Functionality

### Face Detection and Recognition

* Uses InsightFace `buffalo_l` model.
* Supports multiple faces per image.
* Extracts embeddings from detected faces.
* Computes cosine similarity against one or more reference embeddings.
* Configurable similarity threshold.

### Processing Pipeline

1. Load reference images and extract embeddings.
2. Scan each image in the source folder.
3. Detect faces and compute embeddings.
4. Compare embeddings with reference embeddings.
5. Copy matched images to destination folder.
6. Log the process and final statistics in the GUI.

### User Interface

* Tkinter-based desktop GUI.
* Folder selection for source, reference, and output.
* Automatic output folder creation when not provided.
* Live logs in a scrollable text box.
* Threaded processing to keep UI responsive.

### Performance

* Multithreaded image scanning using ThreadPoolExecutor.
* Model caching to avoid repeated initialization.
* Automatic resizing of large images for faster processing.

### Deployment

* Packaged as an executable using PyInstaller.
* Supports optional bundling of InsightFace model files.
* Runs locally on CPU without additional dependencies.

---

## System Requirements

* Windows 10 or later (64-bit)
* 8 CPU cores recommended
* 8 GB RAM recommended
* Sufficient disk space for model files and output
* No Python installation required for the packaged release

---

## Known Limitations

* No EXIF orientation correction.
* No explicit `norm_crop` alignment applied.
* Matching performance depends on input image quality and face pose.
* No progress bar implemented yet.
* No clustering or multi-identity grouping.

---

## Future Improvements

### Preprocessing

* Add EXIF orientation correction.
* Add explicit and consistent face alignment.

### Matching Accuracy

* Add quality checking for low-resolution or blurry faces.
* Improve thresholding strategies.

### Features

* Progress bar and estimated time remaining.
* Extended logging and error reporting.
* Optional GPU support.
* More advanced filtering and pose handling.

### Deployment

* Additional builds for macOS and Linux.
* Enhanced drag-and-drop support in the GUI.
* Web backend using FastAPI.

---

## Usage

1. Launch the application.
2. Select a source image folder.
3. Select a reference image folder.
4. Optionally choose or leave blank the destination folder.
5. Click "Start Process" to begin scanning.
6. Upon completion, matched images will appear in the output folder.

## How to Clone and Use This Repository

### 1. Clone the Repository

Run the following command:

```
git clone https://github.com/your-username/identifyyou.git
```

Then navigate into the project directory:

```
cd IdentifyYou
```

### 2. Install Dependencies (For Developers)

Create a virtual environment:

```
python -m venv venv
```

Activate it:

* Windows:

```
venv\\Scripts\\activate
```

Install dependencies:

```
pip install -r requirements.txt
```

### 3. Running the Application from Source

```
python src/app.py
```

### 4. Building Your Own Executable (Optional)

```
cd src
pyinstaller --noconfirm --onedir --name <app_name> ^
  --hidden-import=insightface ^
  --hidden-import=onnxruntime ^
  app.py
```

The built executable will appear in `dist/IdentifyYou/`.

This README reflects the current implementation of IdentifyYou and will be updated as new features are added.
