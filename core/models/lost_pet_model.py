from sqlalchemy import text
from core.db.db import SessionLocal
from typing import List, Optional
import json
import numpy as np
from PIL import Image
import io
import cloudinary
import cloudinary.uploader
import faiss
import logging
from pathlib import Path
from ultralytics import YOLO
from transformers import AutoImageProcessor, AutoModel
import torch

logger = logging.getLogger(__name__)

YOLO_MODEL = YOLO("yolo11n.pt")

PROCESSOR = AutoImageProcessor.from_pretrained("facebook/dinov2-small")
DINO_MODEL = AutoModel.from_pretrained("facebook/dinov2-small")

EMBEDDING_DIM = 384
PET_CLASSES = {15: "cat", 16: "dog"}


def detect_and_crop_pet(image_bytes: bytes) -> Optional[Image.Image]:
    """
    Detect cat/dog using YOLO11, return highest-confidence crop.
    Returns None if no pet found or error occurs.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        results = YOLO_MODEL(img, conf=0.40, iou=0.45, verbose=False)

        best_crop = None
        best_conf = 0.0

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls)
                if cls_id in PET_CLASSES:
                    conf = float(box.conf)
                    if conf > best_conf and conf >= 0.50:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        crop = img.crop((x1, y1, x2, y2))
                        best_crop = crop
                        best_conf = conf

        return best_crop

    except Exception as e:
        logger.warning(f"YOLO detection failed: {str(e)}")
        return None


def compute_dinov2_embedding(img: Image.Image) -> Optional[List[float]]:
    """
    Compute normalized 384-dim DINOv2-small embedding (CLS token).
    """
    if img is None:
        return None

    try:
        inputs = PROCESSOR(images=img, return_tensors="pt")
        with torch.no_grad():
            outputs = DINO_MODEL(**inputs)
        emb = outputs.last_hidden_state[:, 0].squeeze().cpu().numpy()  # CLS token
        emb = emb / (np.linalg.norm(emb) + 1e-8)
        return emb.tolist()
    except Exception as e:
        logger.warning(f"DINOv2 embedding failed: {str(e)}")
        return None


class LostPetModel:
    FAISS_INDEX_PATH = Path(__file__).parent.parent / "faiss_index" / "pet_embeddings.index"
    _faiss_index = None

    @staticmethod
    def save_lost_pet(pet_type, age_years, days_missing, near_water, posted_on_fb, barangay) -> int:
        session = SessionLocal()
        lost_pet_id = None
        try:
            query = """
                INSERT INTO lost_pets (
                    pet_type, age_years, days_missing, near_water, posted_on_fb, barangay
                ) VALUES (
                    :pet_type, :age_years, :days_missing, :near_water, :posted_on_fb, :barangay
                ) RETURNING id
            """
            result = session.execute(text(query), {
                "pet_type": pet_type,
                "age_years": age_years,
                "days_missing": days_missing,
                "near_water": near_water,
                "posted_on_fb": posted_on_fb,
                "barangay": barangay
            })
            lost_pet_id = result.scalar()
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
        return lost_pet_id

    @staticmethod
    def save_pet_images(lost_pet_id: int, uploaded_files: list) -> List[List[float]]:
        embeddings = []
        if not uploaded_files:
            return embeddings

        for uploaded_file in uploaded_files:
            emb = LostPetModel._save_single_image(lost_pet_id, uploaded_file)
            if emb:
                embeddings.append(emb)
        return embeddings

    @staticmethod
    def _save_single_image(lost_pet_id: int, uploaded_file) -> Optional[List[float]]:
        session = SessionLocal()
        embedding = None
        try:
            if hasattr(uploaded_file, "getbuffer"):
                file_bytes = uploaded_file.getbuffer()
            elif hasattr(uploaded_file, "read"):
                uploaded_file.seek(0)
                file_bytes = uploaded_file.read()
                uploaded_file.seek(0)
            else:
                raise ValueError("Uploaded file must be a file-like object")

            upload_result = cloudinary.uploader.upload(
                io.BytesIO(file_bytes),
                folder="pila_pets_ai",
                resource_type="image"
            )
            image_url = upload_result.get("secure_url")

            cropped = detect_and_crop_pet(file_bytes)
            if cropped is None:
                logger.info("No pet detected → using full image as fallback")
                cropped = Image.open(io.BytesIO(file_bytes)).convert("RGB")

            embedding = compute_dinov2_embedding(cropped)

            if embedding is None or len(embedding) != EMBEDDING_DIM:
                logger.warning(
                    f"Skipping image: invalid embedding (len={len(embedding) if embedding else 'None'}) "
                    f"(expected {EMBEDDING_DIM})"
                )
                return None

            embedding_json = json.dumps(embedding)

            query = """
                INSERT INTO pet_images (lost_pet_id, image_path, embedding)
                VALUES (:lost_pet_id, :image_path, :embedding)
            """
            session.execute(text(query), {
                "lost_pet_id": lost_pet_id,
                "image_path": image_url,
                "embedding": embedding_json
            })
            session.commit()

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save image: {str(e)}")
            raise
        finally:
            session.close()

        return embedding

    @staticmethod
    def get_existing_embeddings() -> List[List[float]]:
        session = SessionLocal()
        embeddings_list = []
        try:
            rows = session.execute(text("SELECT embedding FROM pet_images")).fetchall()
            for r in rows:
                if r.embedding:
                    emb = r.embedding
                    if isinstance(emb, list) and len(emb) == EMBEDDING_DIM:
                        embeddings_list.append(emb)
                    else:
                        logger.warning(f"Skipping invalid embedding (type={type(emb)}, len={len(emb) if emb else 'None'})")
        finally:
            session.close()
        return embeddings_list

    @staticmethod
    def _load_faiss_index():
        if LostPetModel._faiss_index is not None:
            return LostPetModel._faiss_index

        dim = EMBEDDING_DIM

        if not LostPetModel.FAISS_INDEX_PATH.exists():
            logger.info("FAISS index not found → creating new IndexFlatIP (cosine)")
            index = faiss.IndexFlatIP(dim)
            LostPetModel._faiss_index = index
            return index

        index = faiss.read_index(str(LostPetModel.FAISS_INDEX_PATH))
        if index.d != dim:
            logger.warning(f"Existing index dim {index.d} != new {dim} → creating new")
            index = faiss.IndexFlatIP(dim)
        LostPetModel._faiss_index = index
        return index

    @staticmethod
    def compute_similarity(query_embedding: List[float], k: int = 5) -> tuple[List[float], List[int]]:
        """
        Compute cosine similarities using IndexFlatIP.
        Returns top-k similarity scores (0-1) and corresponding indices.
        """
        if len(query_embedding) != EMBEDDING_DIM:
            logger.warning("Query embedding dimension mismatch")
            return [], []

        index = LostPetModel._load_faiss_index()
        if index.ntotal == 0:
            return [], []

        query_vec = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        scores, indices = index.search(query_vec, k)

        valid_mask = indices[0] != -1
        return scores[0][valid_mask].tolist(), indices[0][valid_mask].tolist()


# ────────────────────────────────────────────────────────────────
# Helper for Found Pet feature (used in app.py / controller)
# ────────────────────────────────────────────────────────────────

def compute_embedding_from_upload(uploaded_file) -> Optional[List[float]]:
    """
    Compute DINOv2 embedding from a Streamlit UploadedFile object.
    Reuses the existing YOLO detection + DINOv2 pipeline.
    Returns embedding list or None on failure.
    """
    try:
        # Read bytes (Streamlit UploadedFile)
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)  # Reset pointer for safety

        cropped = detect_and_crop_pet(file_bytes)
        if cropped is None:
            logger.info("No pet detected in uploaded file → fallback to full image")
            cropped = Image.open(io.BytesIO(file_bytes)).convert("RGB")

        embedding = compute_dinov2_embedding(cropped)

        if embedding is None or len(embedding) != EMBEDDING_DIM:
            logger.warning(f"Invalid embedding from upload (len={len(embedding) if embedding else 'None'})")
            return None

        return embedding

    except Exception as e:
        logger.warning(f"Embedding from upload failed: {str(e)}")
        return None