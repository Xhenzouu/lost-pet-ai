# helpers/test_predict_batch.py

import sys
from pathlib import Path
import logging
from pprint import pprint

# -------------------------------
# Add project root to sys.path
# -------------------------------
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.predict import predict_pet_reunion

# -------------------------------
# Configure logging
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("helpers_test_predict_batch.log"),
        logging.StreamHandler()
    ]
)

# -------------------------------
# Batch test function
# -------------------------------
def batch_test(pet_ids):
    print("=== Lost Pet AI — Batch Prediction Test ===\n")
    for pet_id in pet_ids:
        if not isinstance(pet_id, int):
            print(f"❌ Invalid Pet ID: {pet_id}. Skipping.")
            continue

        try:
            result = predict_pet_reunion(pet_id)
            logging.info(f"Prediction for pet ID {pet_id}: {result}")
            print(f"Pet ID {pet_id} Prediction:")
            pprint(result)
            print("\n-----------------------------\n")
        except Exception as e:
            logging.error(f"Prediction failed for pet ID {pet_id}: {e}")
            print(f"❌ Prediction failed for Pet ID {pet_id}: {e}\n")


# -------------------------------
# Run batch test
# -------------------------------
if __name__ == "__main__":
    # Example batch list — you can modify
    pet_ids = [1, 2, 3, 4, 5]
    batch_test(pet_ids)