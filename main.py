from insightface.app import FaceAnalysis
import os
import shutil
import cv2
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

SOURCE_FOLDER = "C:\\Users\\manis\\OneDrive\\Desktop\\test_sample"
DEST_FOLDER = "C:\\Users\\manis\\OneDrive\\Desktop\\manish-farewell-3"
REF_IMG = "C:\\Users\\manis\\OneDrive\\Desktop\\ref"

os.makedirs(DEST_FOLDER, exist_ok=True)
print("Verified/Created destination folder.")

app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=0,det_size=(640,640))
app.models.pop('genderage', None) #drop unnecessary models to save memory and improve speed
app.models.pop('landmark_3d_68', None)
print("Model loaded.")

# Get reference embedding
ref_embeds=[]
ref_paths=[os.path.join(REF_IMG,f) for f in os.listdir(REF_IMG) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
for rp in ref_paths:
    ref_img = cv2.imread(rp)
    ref_face = app.get(ref_img)[0].embedding
    ref_embeds.append(ref_face)

print("Reference embedding extracted.")

def isMatch(emb,ref_embeds,threshold=0.32):
    for ref in ref_embeds:
        cos = np.dot(ref, emb) / (np.linalg.norm(ref) * np.linalg.norm(emb))
        print(f"Cosine similarity: {cos:.4f}")
        if cos > threshold:
            return True
    return False

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
            
            if isMatch(emb, ref_embeds):
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
    with ThreadPoolExecutor(max_workers=8) as executor:
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

