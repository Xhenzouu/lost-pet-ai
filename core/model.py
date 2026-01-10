import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from typing import List, Optional
from .config import BARANGAYS
import faiss
import json
from core.models.lost_pet_model import LostPetModel

BASE_DIR = Path(__file__).resolve().parent
PKL_DIR = BASE_DIR.parent / "pkl"
FAISS_INDEX_PATH = PKL_DIR / "faiss_index.idx"

def load_model_artifacts(v5: bool = True):
    model_file = "lost_pet_model_v5.pkl" if v5 else "lost_pet_model_v4.pkl"
    model_path = PKL_DIR / model_file
    le_barangay_path = PKL_DIR / "le_barangay.pkl"

    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    if not le_barangay_path.exists():
        raise FileNotFoundError(f"LabelEncoder file not found: {le_barangay_path}")

    model = joblib.load(model_path)
    le_barangay = joblib.load(le_barangay_path)
    return model, le_barangay

def bucket_days(days_missing: int) -> int:
    if days_missing <= 3:
        return 0
    elif days_missing <= 7:
        return 1
    elif days_missing <= 14:
        return 2
    else:
        return 3

def compute_unsupervised_prob(
    age: int,
    days_missing: int,
    posted_on_fb: int,
    near_water: int,
    embeddings: Optional[list] = None
) -> float:
    """
    Compute a probability score (0-1) for reunion without a supervised model.
    Uses heuristics: days_missing, FB posting, near water, image similarity.
    """
    if days_missing <= 3:
        days_factor = 1.0
    elif days_missing <= 7:
        days_factor = 0.7
    elif days_missing <= 14:
        days_factor = 0.4
    else:
        days_factor = 0.2

    fb_factor = 1.0 if posted_on_fb else 0.5

    water_factor = 0.9 if near_water else 1.0

    sim_factor = 0.5
    if embeddings:
        existing_embeddings = LostPetModel.get_existing_embeddings()
        if existing_embeddings:
            existing_array = np.array(existing_embeddings).astype("float32")
            new_array = np.array(embeddings).astype("float32")
            existing_array /= np.linalg.norm(existing_array, axis=1, keepdims=True) + 1e-8
            new_array /= np.linalg.norm(new_array, axis=1, keepdims=True) + 1e-8
            sims = np.dot(new_array, existing_array.T)
            max_sim = float(np.max(sims))
            sim_factor += 0.5 * max_sim

    prob = days_factor * 0.4 + fb_factor * 0.4 + sim_factor * 0.2
    prob *= water_factor

    return min(max(prob, 0.0), 1.0)

def build_faiss_index(embeddings: List[List[float]]) -> faiss.IndexFlatIP:
    """
    Build a FAISS index from embeddings list.
    """
    if not embeddings:
        return None
    dim = len(embeddings[0])
    index = faiss.IndexFlatIP(dim)
    emb_array = np.array(embeddings).astype("float32")
    emb_array /= np.linalg.norm(emb_array, axis=1, keepdims=True) + 1e-8
    index.add(emb_array)
    faiss.write_index(index, str(FAISS_INDEX_PATH))
    return index

def load_faiss_index() -> Optional[faiss.IndexFlatIP]:
    if FAISS_INDEX_PATH.exists():
        return faiss.read_index(str(FAISS_INDEX_PATH))
    return None

def query_faiss_index(index: faiss.IndexFlatIP, embedding: List[float], top_k: int = 5):
    """
    Query FAISS index for nearest neighbors.
    Returns distances and indices.
    """
    if index is None or embedding is None:
        return [], []
    emb_array = np.array(embedding).astype("float32").reshape(1, -1)
    emb_array /= np.linalg.norm(emb_array, axis=1, keepdims=True) + 1e-8
    distances, indices = index.search(emb_array, top_k)
    return distances[0].tolist(), indices[0].tolist()

def predict_reunion(
    model,
    le_barangay,
    age: int,
    days_missing: int,
    barangay_input: str,
    near_water: int,
    posted_on_fb: int,
    embeddings: Optional[list] = None
):
    days_bucket = bucket_days(days_missing)
    prob = compute_unsupervised_prob(
        age=age,
        days_missing=days_missing,
        posted_on_fb=posted_on_fb,
        near_water=near_water,
        embeddings=embeddings
    )
    image_count = len(embeddings) if embeddings else 0

    result_text = f"Estimated probability of reunion: {prob:.1%}"

    return {
        "result_text": result_text,
        "probability": prob,
        "days_bucket": days_bucket,
        "image_count": image_count,
        "avg_embedding_norm": float(np.mean([np.linalg.norm(e) for e in embeddings])) if embeddings else None
    }