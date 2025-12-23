# model.py
import pandas as pd
import joblib
from pathlib import Path
from config import BARANGAYS

BASE_DIR = Path(__file__).resolve().parent
PKL_DIR = BASE_DIR / "pkl"

def load_model_artifacts():
    try:
        model = joblib.load(PKL_DIR / "lost_pet_model_v4.pkl")
        le_barangay = joblib.load(PKL_DIR / "le_barangay.pkl")
        return model, le_barangay
    except Exception as e:
        raise FileNotFoundError(f"Model files not found in 'pkl' folder: {e}")

def bucket_days(days):
    if days <= 3:
        return 0
    elif days <= 7:
        return 1
    elif days <= 14:
        return 2
    else:
        return 3

def predict_reunion(model, le_barangay, age, days, barangay_input, near_water, posted_on_fb):
    barangay_lower = barangay_input.strip().lower()
    matches = [b for b in BARANGAYS if barangay_lower in b.lower()]
    if not matches:
        return "Error: Barangay not found. Choose from the list.", None, None
    barangay = matches[0]

    barangay_encoded = le_barangay.transform([barangay])[0]
    days_bucket = bucket_days(days)
    input_df = pd.DataFrame([[age, days, days_bucket, near_water, posted_on_fb, barangay_encoded]],
                            columns=['age_years', 'days_missing', 'days_missing_bucket', 'near_water', 'posted_on_fb', 'barangay_encoded'])
    
    prob = model.predict_proba(input_df)[0][1]
    status = "Likely Found" if prob > 0.5 else "Unlikely Found"
    return f"Probability of being found: {prob:.1%} → {status}", prob, days_bucket