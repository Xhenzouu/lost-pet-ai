import sys
from pathlib import Path
import logging
import numpy as np
import joblib

# -------------------------------
# Add project root to sys.path
# -------------------------------
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.db.db import get_lost_pet
from core.models.lost_pet_model import LostPetModel
from core.model import predict_reunion

# -------------------------------
# Logging setup
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# -------------------------------
# Constants
# -------------------------------
PET_ID_TO_TEST = 1  # Change this to test other pet IDs
MODEL_PATH = PROJECT_ROOT / "core/models/reunion_model.pkl"
LE_BARANGAY_PATH = PROJECT_ROOT / "core/models/le_barangay.pkl"

# -------------------------------
# Load model and label encoder
# -------------------------------
try:
    model = joblib.load(MODEL_PATH)
    le_barangay = joblib.load(LE_BARANGAY_PATH)
    logger.info("✅ ML model and label encoder loaded successfully.")
except Exception as e:
    logger.error(f"❌ Failed to load model or label encoder: {e}")
    model = None
    le_barangay = None

# -------------------------------
# Fetch pet data from DB
# -------------------------------
pet_data = get_lost_pet(PET_ID_TO_TEST)
if not pet_data:
    logger.error(f"Pet ID {PET_ID_TO_TEST} not found.")
    exit(1)

logger.info(f"Fetched pet ID {PET_ID_TO_TEST} with {len(pet_data['embeddings'])} embeddings.")

# -------------------------------
# Call predict_reunion
# -------------------------------
raw_prediction = predict_reunion(
    model=model,
    le_barangay=le_barangay,
    age=pet_data["age"],
    days_missing=pet_data["days_missing"],
    barangay_input=pet_data["barangay"],
    near_water=pet_data["near_water"],
    posted_on_fb=pet_data["posted_on_fb"]
)

# -------------------------------
# Detect return type and extract probability
# -------------------------------
if isinstance(raw_prediction, dict):
    reunion_chance = raw_prediction.get("reunion_chance", 0.0)
    reasons = raw_prediction.get("reasons", [])
    recommended_actions = raw_prediction.get("recommended_actions", [])
elif isinstance(raw_prediction, (float, int)):
    reunion_chance = float(raw_prediction)
    reasons = []
    recommended_actions = []
else:
    reunion_chance = 0.0
    reasons = []
    recommended_actions = []

# -------------------------------
# Display results
# -------------------------------
print("\n===== DB-DRIVEN TEST RESULT =====\n")
print(f"Lost Pet ID: {PET_ID_TO_TEST}")
print(f"Result: {reunion_chance:.1f}%\n")

if reasons:
    print("Reasons:")
    for reason in reasons:
        print(f" - {reason}")

if recommended_actions:
    print("\nRecommended actions:")
    for action in recommended_actions:
        print(f" - {action}")

print(f"\nImages used: {len(pet_data['embeddings'])}")

# -------------------------------
# Compute FAISS similarity using all embeddings
# -------------------------------
similar_scores = {}
for idx, pet_embedding in enumerate(pet_data["embeddings"]):
    try:
        score, neighbor_idx = LostPetModel.compute_similarity(pet_embedding, k=1)
        if neighbor_idx is not None:
            if neighbor_idx not in similar_scores or score > similar_scores[neighbor_idx]:
                similar_scores[neighbor_idx] = score
    except Exception as e:
        logger.warning(f"Failed similarity for embedding {idx}: {e}")

# -------------------------------
# Display top similar pets safely
# -------------------------------
if similar_scores:
    top_similar = sorted(similar_scores.items(), key=lambda x: x[1], reverse=True)
    print("\nTop similar pets:")
    for neighbor_idx, score in top_similar:
        print(f" - Pet ID: {neighbor_idx}, similarity: {score:.4f}")
else:
    print("\nNo similar pets found in the FAISS index.")

# -------------------------------
# Overall similarity
# -------------------------------
if pet_data["embeddings"]:
    all_scores = list(similar_scores.values())
    overall_similarity = max(all_scores) if all_scores else 0.0
    print(f"\nOverall similarity score: {overall_similarity:.4f}")