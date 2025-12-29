# core/predict.py

import sys
import logging
import numpy as np
from .db.db import get_lost_pet
from .model import load_model_artifacts, predict_reunion
from .models.lost_pet_model import LostPetModel
from numpy.linalg import norm

# -------------------------------
# Configure logging (UTF-8 safe)
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("predict.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

def cosine_similarity(vec_a, vec_b):
    """
    Compute cosine similarity between two vectors.
    """
    vec_a = np.array(vec_a)
    vec_b = np.array(vec_b)
    if vec_a.size == 0 or vec_b.size == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm(vec_a) * norm(vec_b) + 1e-8))

def compute_max_similarity(embeddings: list):
    """
    Compute the max similarity between uploaded embeddings and existing database embeddings.
    """
    if not embeddings:
        return None

    existing_embeddings = LostPetModel.get_existing_embeddings()
    if not existing_embeddings:
        return None

    max_sims = []
    for emb in embeddings:
        sims = [cosine_similarity(emb, db_emb) for db_emb in existing_embeddings]
        max_sims.append(max(sims) if sims else 0.0)

    return max(max_sims) if max_sims else None

def predict_pet_reunion(pet_id: int, use_v5: bool = True):
    """
    Predict pet reunion probability using v5 model by default.
    Returns dict compatible with interpret_prediction.
    """
    pet = get_lost_pet(pet_id)
    if not pet:
        msg = f"Lost pet with ID {pet_id} not found."
        logging.warning(msg)
        return {"error": msg}

    required_fields = ["age", "days_missing", "barangay", "near_water", "posted_on_fb", "embeddings", "pet_name"]
    for field in required_fields:
        if field not in pet:
            msg = f"Missing required field '{field}' for pet ID {pet_id}."
            logging.error(msg)
            return {"error": msg}

    # Load v5 RandomForest model + LabelEncoder
    model, le_barangay = load_model_artifacts(v5=use_v5)

    try:
        prediction = predict_reunion(
            model=model,
            le_barangay=le_barangay,
            age=pet["age"],
            days_missing=pet["days_missing"],
            barangay_input=pet["barangay"],
            near_water=pet["near_water"],
            posted_on_fb=pet["posted_on_fb"],
            embeddings=pet.get("embeddings", [])
        )

        # Compute embedding similarity
        max_similarity = compute_max_similarity(pet.get("embeddings", []))
        if max_similarity is not None:
            prediction["max_similarity"] = max_similarity
            prediction["result_text"] += f" | Max Image Similarity: {max_similarity:.1%}"

        logging.info(f"Prediction for pet ID {pet_id} ({pet['pet_name']}): {prediction['result_text']}")
    except Exception as e:
        msg = f"Prediction failed for pet ID {pet_id}: {str(e)}"
        logging.error(msg)
        return {"error": msg}

    # Flatten final dict for Streamlit / interpret_prediction
    result = {
        "pet_id": pet_id,
        "pet_name": pet["pet_name"],
        **prediction,
        "embeddings_count": len(pet.get("embeddings", []))
    }
    return result

# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    pet_id = 1
    result = predict_pet_reunion(pet_id)
    print(result)