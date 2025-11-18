from insightface.app import FaceAnalysis
import os
import shutil
import cv2
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

SOURCE_FOLDER = "C:\\Users\\manis\\OneDrive\\Desktop\\test_sample"
DEST_FOLDER = "C:\\Users\\manis\\OneDrive\\Desktop\\manish-farewell-3"
REF_IMG = "C:\\Users\\manis\\Downloads\\manish.jpg"

os.makedirs(DEST_FOLDER, exist_ok=True)
print("Verified/Created destination folder.")

app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=0)
app.models.pop('genderage', None) #drop unnecessary models to save memory and improve speed
app.models.pop('landmark_3d_68', None)
print("Model loaded.")

# Get reference embedding
ref = cv2.imread(REF_IMG)
ref_face = app.get(ref)[0].embedding
print("Reference embedding extracted.")

def process_image(img_path):
    """Process single image and return path if match found"""
    try:
        img = cv2.imread(img_path)
        if img is None:
            print(f"Failed to load: {img_path}")
            return None
        
        h, w = img.shape[:2]
        scale = 1024 / max(h, w)
        if scale < 1:
            img = cv2.resize(img, (int(w * scale), int(h * scale)))
        
        faces = app.get(img)
        filename = os.path.basename(img_path)
        print(f"[{filename}] Found {len(faces)} face(s)")
        
        for idx, face in enumerate(faces):
            emb = face.embedding
            cos = np.dot(ref_face, emb) / (np.linalg.norm(ref_face) * np.linalg.norm(emb))
            print(f"[{filename}] Face {idx+1}: similarity={cos:.4f}")
            
            if cos > 0.32:
                print(f"MATCH: {filename}")
                return img_path
        
        return None
        
    except Exception as e:
        print(f"Error processing {img_path}: {e}")
        return None

if __name__ == "__main__":
    image_paths = [
        os.path.join(SOURCE_FOLDER, f)
        for f in os.listdir(SOURCE_FOLDER)
        if f.lower().endswith((".jpg", ".png", ".jpeg"))
    ]
    
    print(f"\nProcessing {len(image_paths)} images...\n")
    start = time.time()
    
    
    matched_count = 0
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(process_image, path): path for path in image_paths}
        
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                shutil.copy(result, DEST_FOLDER)
                matched_count += 1
    
    end = time.time()
    
    print(f"\n{'='*60}")
    print(f"Completed: {matched_count}/{len(image_paths)} matches found")
    print(f"Time taken: {end - start:.2f}s")
    print(f"{'='*60}")

# from insightface.app import FaceAnalysis
# import os
# import shutil
# import cv2
# import numpy as np
# import time

# SOURCE_FOLDER="C:\\Users\\manis\\OneDrive\\Desktop\\test_sample"
# DEST_FOLDER="C:\\Users\\manis\\OneDrive\\Desktop\\manish-farewell-3"
# REF_IMG="C:\\Users\\manis\\Downloads\\manish.jpg"

# os.makedirs(DEST_FOLDER,exist_ok=True)
# print("Verified/Created destination folder.")
# app=FaceAnalysis(name="buffalo_l")
# app.prepare(ctx_id=0)
# app.models.pop('genderage', None)
# app.models.pop('landmark_3d_68', None)
# print("Model loaded.")

# ref=cv2.imread(REF_IMG)
# ref_face=app.get(ref)[0].embedding

# print("About to iterate through source folder images...")

# start=time.time()

# for f in os.listdir(SOURCE_FOLDER):
#     if not f.lower().endswith((".jpg", ".png", ".jpeg")):
#         continue

#     img_path = os.path.join(SOURCE_FOLDER, f)
#     img = cv2.imread(img_path)

#     h, w = img.shape[:2]

#     scale = 1024 / max(h, w)
#     img = cv2.resize(img, (int(w * scale), int(h * scale)))

#     print("About to iterate through faces in image:", f)
#     faces = app.get(img)
#     print(f"Found {len(faces)} faces in image: {f}")
#     for face in faces:
#         emb = face.embedding

#         #cosine similarity over euclidean distance
#         cos = np.dot(ref_face, emb) / (np.linalg.norm(ref_face) * np.linalg.norm(emb))

#         print("Cosine:", cos)

#         if cos > 0.32:   # threshold
#             shutil.copy(img_path, DEST_FOLDER)
#             print("MATCHED:", f)
#             break
#         else:
#             print("No match for face in image:", f)
# end=time.time()

# print(f"Time taken: {end - start:.2f}s")
