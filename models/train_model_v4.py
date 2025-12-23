import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

BASE_DIR = Path(__file__).resolve().parent.parent

# Load dataset
df = pd.read_csv(BASE_DIR / "csv" / "lost_pets_pila_dataset.csv")

# 🔥 Feature engineering: days_missing_bucket
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

# Encode barangay
le_barangay = LabelEncoder()
df["barangay_encoded"] = le_barangay.fit_transform(df["barangay"])

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

# Train model
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(X, y)

# Save artifacts in pkl folder
joblib.dump(model, BASE_DIR / "pkl" / "lost_pet_model_v4.pkl")
joblib.dump(le_barangay, BASE_DIR / "pkl" / "le_barangay.pkl")

print("✅ Model v4 trained with days_missing_bucket feature")
