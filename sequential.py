from insightface.app import FaceAnalysis
import os
import shutil
import cv2
import numpy as np
import time

SOURCE_FOLDER="C:\\Users\\manis\\OneDrive\\Desktop\\test_sample"
DEST_FOLDER="C:\\Users\\manis\\OneDrive\\Desktop\\manish-farewell-3"
REF_IMG="C:\\Users\\manis\\Downloads\\manish.jpg"

os.makedirs(DEST_FOLDER,exist_ok=True)
print("Verified/Created destination folder.")
app=FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=0)
app.models.pop('genderage', None)
app.models.pop('landmark_3d_68', None)
print("Model loaded.")

ref=cv2.imread(REF_IMG)
ref_face=app.get(ref)[0].embedding

print("About to iterate through source folder images...")

start=time.time()

for f in os.listdir(SOURCE_FOLDER):
    if not f.lower().endswith((".jpg", ".png", ".jpeg")):
        continue

    img_path = os.path.join(SOURCE_FOLDER, f)
    img = cv2.imread(img_path)

    h, w = img.shape[:2]

    scale = 1024 / max(h, w)
    img = cv2.resize(img, (int(w * scale), int(h * scale)))

    print("About to iterate through faces in image:", f)
    faces = app.get(img)
    print(f"Found {len(faces)} faces in image: {f}")
    for face in faces:
        emb = face.embedding

        #cosine similarity over euclidean distance
        cos = np.dot(ref_face, emb) / (np.linalg.norm(ref_face) * np.linalg.norm(emb))

        print("Cosine:", cos)

        if cos > 0.32:   # threshold
            shutil.copy(img_path, DEST_FOLDER)
            print("MATCHED:", f)
            break
        else:
            print("No match for face in image:", f)
end=time.time()

print(f"Time taken: {end - start:.2f}s")