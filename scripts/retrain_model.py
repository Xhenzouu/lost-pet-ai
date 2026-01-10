# scripts/retrain_model.py
"""
Retrain LostPetModel v5 using all rows from lost_pets and pet_images.
Saves:
- core/pkl/lost_pet_model_v5.pkl
- core/pkl/le_barangay.pkl
"""

import os
import numpy as np
import pandas as pd
import joblib
from sqlalchemy import create_engine, text
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from dotenv import load_dotenv

# -------------------------------
# Load .env
# -------------------------------
load_dotenv()

DB_URL = os.getenv("DB_URL_LOCAL") or os.getenv("DB_URL_PROD")  # change ENV vars for local/prod
EMBEDDING_SIZE = 512  # same as compute_color_histogram_embedding

# -------------------------------
# Setup SQLAlchemy engine
# -------------------------------
engine = create_engine(DB_URL, future=True)

# -------------------------------
# 1. Load lost_pets table
# -------------------------------
with engine.connect() as conn:
    pets_df = pd.read_sql("SELECT * FROM lost_pets", conn)

# -------------------------------
# 2. Load and average pet_images embeddings
# -------------------------------
embeddings_dict = {}

with engine.connect() as conn:
    rows = conn.execute(text("SELECT lost_pet_id, embedding FROM pet_images")).fetchall()
    for r in rows:
        if r.embedding:
            # Fix: handle list directly without json.loads
            if isinstance(r.embedding, str):
                # If somehow it's still a string, convert
                emb_list = eval(r.embedding)  # careful, only works if safe!
            else:
                emb_list = r.embedding
            embeddings_dict.setdefault(r.lost_pet_id, []).append(emb_list)

avg_embeddings = {pet_id: np.mean(np.array(embs), axis=0)
                  for pet_id, embs in embeddings_dict.items()}

# -------------------------------
# 3. Build features X
# -------------------------------
X_list = []
for _, row in pets_df.iterrows():
    features = [
        row['age_years'],
        row['days_missing'],
        int(row['near_water']),
        int(row['posted_on_fb']),
        row['barangay'],  # will encode later
    ]
    emb = avg_embeddings.get(row['id'], np.zeros(EMBEDDING_SIZE))
    features.extend(emb)
    X_list.append(features)

X = pd.DataFrame(X_list)

# -------------------------------
# 4. Encode barangay
# -------------------------------
le_barangay = LabelEncoder()
X[4] = le_barangay.fit_transform(X[4])

# -------------------------------
# 5. Build labels y
# -------------------------------
y = pets_df['found'].astype(int).values  # 1 = found, 0 = not found

# -------------------------------
# 6. Train RandomForest
# -------------------------------
clf = RandomForestClassifier(
    n_estimators=500,
    max_depth=None,
    random_state=42,
    class_weight='balanced'
)
clf.fit(X, y)

# -------------------------------
# 7. Save model and LabelEncoder
# -------------------------------
pkl_dir = os.path.join(os.path.dirname(__file__), "pkl")
os.makedirs(pkl_dir, exist_ok=True)

joblib.dump(clf, os.path.join(pkl_dir, "lost_pet_model_v5.pkl"))
joblib.dump(le_barangay, os.path.join(pkl_dir, "le_barangay.pkl"))

print(f"✅ Model retrained and saved: {len(X)} samples used.")