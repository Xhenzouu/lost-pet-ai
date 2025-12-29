# helpers/test_predict.py

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
        logging.FileHandler("helpers_test_predict.log"),
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
# Interactive test function
# -------------------------------
def interactive_test():
    print("=== Lost Pet AI — Interactive Prediction Test ===\n")
    while True:
        user_input = input("Enter Pet ID (or 'q' to quit): ").strip()
        if user_input.lower() == "q":
            print("Exiting interactive test.")
            break

        if not user_input.isdigit():
            print("❌ Invalid input. Please enter a numeric Pet ID.\n")
            continue

        pet_id = int(user_input)
        try:
            result = predict_pet_reunion(pet_id)
            logging.info(f"Interactive prediction for pet ID {pet_id}: {result}")
            pprint(result)
            print("\n-----------------------------\n")
        except Exception as e:
            logging.error(f"Interactive prediction failed for pet ID {pet_id}: {e}")
            print(f"❌ Prediction failed for Pet ID {pet_id}: {e}\n")

# -------------------------------
# Run helper
# -------------------------------
if __name__ == "__main__":
    mode = input("Select mode: [1] Batch, [2] Interactive: ").strip()
    if mode == "1":
        # Example batch — modify as needed
        pet_ids = [1, 2, 3, 4, 5]
        batch_test(pet_ids)
    elif mode == "2":
        interactive_test()
    else:
        print("❌ Invalid selection. Exiting.")