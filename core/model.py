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
    """
    Predict lost pet reunion probability.
    Returns dictionary with numeric probability and embedding info.
    """

    # -------------------------------
    # Clean and match barangay
    # -------------------------------
    barangay_clean = barangay_input.strip()
    if barangay_clean not in BARANGAYS:
        # Try case-insensitive match
        matched = [b for b in BARANGAYS if b.lower() == barangay_clean.lower()]
        if not matched:
            return {
                "result_text": "Error: Barangay not found. Please choose a valid barangay.",
                "probability": 0.0,
                "days_bucket": bucket_days(days_missing),
                "image_count": len(embeddings) if embeddings else 0,
                "avg_embedding_norm": None
            }
        barangay_clean = matched[0]

    # Encode barangay
    try:
        barangay_encoded = int(le_barangay.transform([barangay_clean])[0])
    except Exception:
        # fallback if label encoding fails
        barangay_encoded = 0

    # -------------------------------
    # Days missing → bucket
    # -------------------------------
    days_bucket = bucket_days(days_missing)

    # -------------------------------
    # Prepare model input
    # -------------------------------
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
    result_text = f"Probability of being found: {prob:.1%} → {status}"

    # -------------------------------
    # Embeddings info
    # -------------------------------
    image_count = len(embeddings) if embeddings else 0
    avg_embedding_norm = None
    if embeddings:
        norms = [np.linalg.norm(e) for e in embeddings if e]
        if norms:
            avg_embedding_norm = float(np.mean(norms))

    return {
        "result_text": result_text,
        "probability": prob,
        "days_bucket": days_bucket,
        "image_count": image_count,
        "avg_embedding_norm": avg_embedding_norm
    }