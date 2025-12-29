# core/model.py

import pandas as pd
import joblib
import numpy as np
from pathlib import Path
from typing import List, Optional
from .config import BARANGAYS

# -------------------------------
# Paths
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent
PKL_DIR = BASE_DIR.parent / "pkl"

# -------------------------------
# Load Model Artifacts (v5)
# -------------------------------
def load_model_artifacts(v5: bool = True):
    """
    Load ML model artifacts.
    Default is v5 for public use.
    """
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

# -------------------------------
# Days Missing → Bucket
# -------------------------------
def bucket_days(days_missing: int) -> int:
    if days_missing <= 3:
        return 0
    elif days_missing <= 7:
        return 1
    elif days_missing <= 14:
        return 2
    else:
        return 3

# -------------------------------
# Predict Reunion (v5)
# -------------------------------
def predict_reunion(
    model,
    le_barangay,
    age: int,
    days_missing: int,
    barangay_input: str,
    near_water: int,
    posted_on_fb: int,
    embeddings: Optional[List[List[float]]] = None
):
    """
    Predict lost pet reunion probability.
    Returns a dictionary suitable for interpret_prediction (v5).
    """
    barangay_clean = barangay_input.strip().lower()
    matched_barangays = [b for b in BARANGAYS if barangay_clean in b.lower()]
    if not matched_barangays:
        return {
            "result_text": "Error: Barangay not found. Please choose a valid barangay.",
            "probability": None,
            "days_bucket": None,
            "image_count": 0,
            "avg_embedding_norm": None
        }

    barangay = matched_barangays[0]
    barangay_encoded = int(le_barangay.transform([barangay])[0])
    days_bucket = bucket_days(days_missing)

    input_df = pd.DataFrame(
        [[age, days_missing, days_bucket, near_water, posted_on_fb, barangay_encoded]],
        columns=[
            "age_years", "days_missing", "days_missing_bucket",
            "near_water", "posted_on_fb", "barangay_encoded"
        ]
    )

    # -------------------------------
    # Predict probability
    # -------------------------------
    prob = float(model.predict_proba(input_df)[0][1])
    status = "Likely Found" if prob > 0.5 else "Unlikely Found"

    # -------------------------------
    # Embeddings info
    # -------------------------------
    image_count = 0
    avg_embedding_norm = None
    if embeddings:
        image_count = len(embeddings)
        norms = [np.linalg.norm(e) for e in embeddings if e]
        if norms:
            avg_embedding_norm = float(np.mean(norms))

    result_text = f"Probability of being found: {prob:.1%} → {status}"

    return {
        "result_text": result_text,
        "probability": prob,
        "days_bucket": days_bucket,
        "image_count": image_count,
        "avg_embedding_norm": avg_embedding_norm
    }