# Face Search Tool

## Overview
This project identifies and extracts all images from a directory that contain a specific person's face. A reference image is provided, and the tool scans each image in the target directory, detects all faces, computes face embeddings, compares them to the reference embedding using cosine similarity, and copies the matched images to an output folder.

The current implementation uses the InsightFace `buffalo_l` model for detection and recognition. Face embeddings are generated directly from the detected faces as returned by InsightFace without additional alignment steps. Cosine similarity is used as the matching metric, with a configurable threshold to determine if two faces belong to the same person. 

Image preprocessing presently consists only of resizing and format handling. EXIF orientation correction and explicit landmark-based alignment (`norm_crop`) have not yet been implemented. Images are processed sequentially on CPU, with detection and embedding extraction computed fresh for each run.

---

## Current Approach

### 1. Preprocessing
- Simple resizing of input images to a fixed maximum dimension for efficiency.
- No EXIF orientation correction yet.
- No facial alignment applied to reference or scanned images.

### 2. Face Detection
- InsightFace `buffalo_l` (SCRFD) is used to detect faces.
- Multiple faces per image are supported.
- Detector returns bounding boxes, detection scores, and landmarks.

### 3. Embedding Extraction
- Embeddings are taken directly from the detector’s aligned internal pipeline.
- A single reference embedding is generated from the reference image.

### 4. Similarity Scoring
- Cosine similarity is computed between the reference embedding and each detected face embedding.
- A threshold determines whether a face matches the reference.

### 5. Output Handling
- Images containing at least one matching embedding are copied to the destination folder.
- The process logs match results and similarity scores.

---

## Improvements To Be Done

### Image Preprocessing
- Add EXIF orientation correction.
- Add consistent face alignment using `norm_crop`.

### Matching Accuracy
- Support multiple reference images.
- Implement adaptive or data-driven thresholding.
- Add quality filtering for blurred or low-resolution faces.

### Performance
- Add parallel processing for multiple images.
- Cache embeddings to avoid recomputation.
- Use faster face detectors when needed.

### Robustness
- Handle extreme pose variations more reliably.
- Add fallback alignment strategies.
- Support face frontalization for heavily angled faces.

### Application Features
- Add progress indicators.
- Add GUI interface.
- Add clustering to group all unique identities in the dataset.

### Deployment
- Package the tool as an executable.
- Build a FastAPI backend for web use.
- Add drag-and-drop support for desktop applications.

