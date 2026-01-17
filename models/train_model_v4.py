import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import pandas as pd
import joblib   
from sqlalchemy import text
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from core import SessionLocal

PKL_DIR = BASE_DIR / "pkl"
PKL_DIR.mkdir(exist_ok=True)

def bucket_days(days):
    if days <= 3:
        return 0
    elif days <= 7:
        return 1
    elif days <= 14:
        return 2
    else:
        return 3

print("📥 Loading training data from PostgreSQL...")

session = SessionLocal()

query = text("""
    SELECT
        age_years,
        days_missing,
        near_water,
        posted_on_fb,
        barangay,
        found
    FROM lost_pets
    WHERE found IS NOT NULL
""")

df = pd.read_sql(query, session.bind)
session.close()

if df.empty:
    raise ValueError("❌ No training data found in database.")

print(f"✅ Loaded {len(df)} rows")

df["days_missing_bucket"] = df["days_missing"].apply(bucket_days)

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

print("🧠 Training RandomForest model...")

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(X, y)

joblib.dump(model, PKL_DIR / "lost_pet_model_v4.pkl")
joblib.dump(le_barangay, PKL_DIR / "le_barangay.pkl")

print("✅ Model v4 retrained from PostgreSQL and saved to pkl/")