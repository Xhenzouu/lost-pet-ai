import pandas as pd
import joblib
from sklearn.metrics import classification_report, confusion_matrix
from pathlib import Path

# Get project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

print("Loading dataset...")
df = pd.read_csv(BASE_DIR / "csv" / "lost_pets_pila_dataset.csv")

# Load model and encoder
print("Loading model and encoder...")
model = joblib.load(BASE_DIR / "pkl" / "lost_pet_model_v4.pkl")
le_barangay = joblib.load(BASE_DIR / "pkl" / "le_barangay.pkl")

# Encode barangay
df["barangay_encoded"] = le_barangay.transform(df["barangay"])

features = [
    "age_years",
    "days_missing",
    "days_missing_bucket",
    "near_water",
    "posted_on_fb",
    "barangay_encoded"
]

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

X = df[features]
y = df["found"]

print("\nEvaluating model...\n")

y_pred = model.predict(X)

print("CONFUSION MATRIX")
print(confusion_matrix(y, y_pred))

print("\nCLASSIFICATION REPORT")
print(classification_report(y, y_pred, digits=3))
