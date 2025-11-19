import os
import sys
import time
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import cv2
import numpy as np
from insightface.app import FaceAnalysis

def resource_path(relative_path):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)

#cache model
_APP = None
def get_face_app(model_root=None, ctx_id=0, det_size=(640,640), logger=None):
    global _APP
    if _APP is not None:
        return _APP

    if logger:
        logger("Initializing FaceAnalysis...")
    app = FaceAnalysis(name="buffalo_l")
    try:
        if model_root:
            app.prepare(ctx_id=ctx_id, det_size=det_size, model_root=model_root)
        else:
            app.prepare(ctx_id=ctx_id, det_size=det_size)
    except TypeError:
        if logger:
            logger("prepare() didn't accept model_root; using fallback prepare().")
        app.prepare(ctx_id=ctx_id, det_size=det_size)

    try:
        app.models.pop("genderage", None)
        app.models.pop("landmark_3d_68", None)
    except Exception:
        pass

    _APP = app
    if logger:
        logger("FaceAnalysis is ready.")
    return _APP

def _is_image_file(fn):
    fn = fn.lower()
    return fn.endswith((".jpg", ".jpeg", ".png"))

def _cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def run_work(source_folder,
             dest_folder,
             ref_folder,
             log_callback=None,
             threshold=0.32,
             max_workers=8,
             use_bundled_models=True,
             ctx_id=0,
             det_size=(640,640)):
    """
    Run identification job. Callable from GUI.
    log_callback: function(str) to receive log lines.
    Returns: dict with success, matched, total, time, dest
    """
    logger = log_callback or (lambda s: print(s, flush=True))
    start_time = time.time()

    if not os.path.isdir(source_folder):
        logger(f"ERROR: source folder not found: {source_folder}", color="error")
        return {"success": False, "reason": "source_missing"}

    if not os.path.isdir(ref_folder):
        logger(f"ERROR: reference folder not found: {ref_folder}", color="error")
        return {"success": False, "reason": "ref_missing"}

    os.makedirs(dest_folder, exist_ok=True)
    logger(f"Verified/created destination folder: {dest_folder}", color="info")

    model_root = None
    if use_bundled_models:
        candidate = resource_path("models")
        if os.path.isdir(candidate):
            model_root = candidate
            logger(f"Using bundled models at: {model_root}", color="info")
        else:
            logger("No bundled models found; InsightFace may download models on first run.", color="warning")

    logger("Loading model (this may take several seconds)...", color="info")
    app = get_face_app(model_root=model_root, ctx_id=ctx_id, det_size=det_size, logger=logger)
    logger("Model loaded.", color="info")

    #load references
    ref_files = [f for f in os.listdir(ref_folder) if _is_image_file(f)]
    if not ref_files:
        logger("ERROR: no reference images found.", color="error")
        return {"success": False, "reason": "no_ref_images"}

    ref_embeds = []
    for fname in ref_files:
        path = os.path.join(ref_folder, fname)
        img = cv2.imread(path)
        if img is None:
            logger(f"WARNING: cannot read reference image: {path}", color="warning")
            continue
        faces = app.get(img)
        if not faces:
            logger(f"WARNING: no face found in reference image: {path}", color="warning")
            continue
        ref_embeds.append(faces[0].embedding)
        logger(f"Loaded reference: {fname}", color="info")

    if not ref_embeds:
        logger("ERROR: no valid reference embeddings extracted.", color="error")
        return {"success": False, "reason": "no_ref_embeddings"}

    def is_match(emb):
        best = -1.0
        for ref in ref_embeds:
            cos = _cosine_similarity(ref, emb)
            if cos > best:
                best = cos
            if cos > threshold:
                return True, cos
        return False, best

    def process_image(img_path):
        try:
            img = cv2.imread(img_path)
            if img is None:
                logger(f"Failed to load: {img_path}", color="warning")
                return None
            h, w = img.shape[:2]
            scale = 1024 / max(h, w)
            if scale < 1:
                img = cv2.resize(img, (int(w * scale), int(h * scale)))
            faces = app.get(img)
            filename = os.path.basename(img_path)
            logger(f"[{filename}] Found {len(faces)} face(s)", color="info")
            for idx, face in enumerate(faces):
                emb = face.embedding
                matched, score = is_match(emb)
                logger(f"  face#{idx} cosine={score:.4f}")
                if matched:
                    logger(f"  MATCH: {filename}", color="success")
                    return img_path
            return None
        except Exception as e:
            logger(f"Error processing {img_path}: {e}", color="error")
            return None

    image_paths = [os.path.join(source_folder, f) for f in os.listdir(source_folder) if _is_image_file(f)]
    logger(f"Processing {len(image_paths)} images...", color="info")
    matched_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_image, p): p for p in image_paths}
        for future in as_completed(futures):
            res = future.result()
            if res:
                try:
                    shutil.copy(res, dest_folder)
                    matched_count += 1
                except Exception as e:
                    logger(f"Failed to copy {res} -> {dest_folder}: {e}", color="error")

    elapsed = time.time() - start_time
    logger("\n" + "="*40, color="info")
    logger(f"Completed: {matched_count}/{len(image_paths)} matches found", color="info")
    logger(f"Time taken: {elapsed:.2f}s", color="info")
    logger("="*40, color="info")

    return {"success": True, "matched": matched_count, "total": len(image_paths), "time": elapsed, "dest": dest_folder}

#test via terminal
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--dest", required=True)
    p.add_argument("--ref", required=True)
    p.add_argument("--workers", type=int, default=8)
    args = p.parse_args()

    def _printlog(s): print(s, flush=True)

    res = run_work(args.source, args.dest, args.ref, log_callback=_printlog, max_workers=args.workers)
    if not res.get("success"):
        sys.exit(1)
    sys.exit(0)

