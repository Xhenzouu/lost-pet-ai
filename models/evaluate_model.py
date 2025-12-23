import pandas as pd
import joblib
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix

# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
PKL_DIR = BASE_DIR / "pkl"

print("Loading dataset...")
df = pd.read_csv(BASE_DIR / "csv" / "lost_pets_pila_dataset.csv")

print("Loading model and encoder...")
model = joblib.load(PKL_DIR / "lost_pet_model_v4.pkl")
le_barangay = joblib.load(PKL_DIR / "le_barangay.pkl")

# Encode barangay
df["barangay_encoded"] = le_barangay.transform(df["barangay"])

# Feature engineering: days_missing_bucket
def bucket_days(days):
    if days <= 3:
        return 0
    elif days <= 7:
        return 1
    elif days <= 14:
        return 2
    else:
        return 3

df["days_missing_bucket"] = df["days_missing"].apply(bucket_days)

# Features
features = [
    "age_years",
    "days_missing",
    "days_missing_bucket",
    "near_water",
    "posted_on_fb",
    "barangay_encoded"
]

X = df[features]
y = df["found"]

print("\nEvaluating model...\n")

y_pred = model.predict(X)

print("CONFUSION MATRIX")
print(confusion_matrix(y, y_pred))

print("\nCLASSIFICATION REPORT")
print(classification_report(y, y_pred, digits=3))