# test_submission.py
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.controllers.app_controller import AppController

# ---------------------------
# Optional: load local .env
# ---------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

# ---------------------------
# Instantiate controller
# ---------------------------
controller = AppController()

# ---------------------------
# Sample test submission
# ---------------------------
test_input = {
    "pet_type": "Hamster",
    "age": 2.0,
    "days": 3,
    "barangay": "Pansol",
    "near_water": "Yes",
    "posted_on_fb": "Yes",
    "uploaded_files": []  # put file paths here if you want to test embeddings
}

# ---------------------------
# Run prediction
# ---------------------------
result = controller.handle_submission(
    pet_type=test_input["pet_type"],
    age=test_input["age"],
    days=test_input["days"],
    barangay=test_input["barangay"],
    near_water=test_input["near_water"],
    posted_on_fb=test_input["posted_on_fb"],
    uploaded_files=test_input["uploaded_files"]
)

# ---------------------------
# Show results
# ---------------------------
print("\n===== TEST SUBMISSION RESULT =====\n")
print(f"Result text: {result['result_text']}")
print(f"Reasons:")
for r in result["reasons"]:
    print(f" - {r}")
print(f"Recommended actions:")
for a in result["actions"]:
    print(f" - {a}")
print(f"Number of images processed: {result['num_images']}")