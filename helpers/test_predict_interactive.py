# helpers/test_predict_interactive.py

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
        logging.FileHandler("helpers_test_predict_interactive.log"),
        logging.StreamHandler()
    ]
)

# -------------------------------
# Interactive test loop
# -------------------------------
def interactive_test():
    print("=== Lost Pet AI — Interactive Prediction Test ===")
    print("Enter pet IDs to test. Type 'exit' to quit.\n")

    while True:
        pet_id_input = input("Enter Pet ID: ").strip()
        if pet_id_input.lower() in ["exit", "quit"]:
            print("Exiting...")
            break

        if not pet_id_input.isdigit():
            print("❌ Invalid input. Please enter a numeric Pet ID.")
            continue

        pet_id = int(pet_id_input)

        try:
            result = predict_pet_reunion(pet_id)
            logging.info(f"Prediction for pet ID {pet_id}: {result}")
            print("\nPrediction Result:")
            pprint(result)
            print("\n-----------------------------\n")
        except Exception as e:
            logging.error(f"Prediction failed for pet ID {pet_id}: {e}")
            print(f"❌ Prediction failed: {e}\n")


# -------------------------------
# Run interactive loop
# -------------------------------
if __name__ == "__main__":
    interactive_test()