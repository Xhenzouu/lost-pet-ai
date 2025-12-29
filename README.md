# Lost Pet Reunion AI – Pila, Laguna 🐕🐈🐇🐦🐢

A machine learning–powered community project that predicts the likelihood of a lost pet being reunited with its owner in **Pila, Laguna, Philippines**.

Designed for real-world public use, this system prioritizes:

- 🧠 High recall (don’t miss pets that are likely to be found)
- 👥 Simplicity and clarity for non-technical users
- 🔮 Extensibility for future AI upgrades (vision + similarity search)

Current production version: **v5 (Public Release)**

🔗 **Live Demo:**  
https://lost-pet-ai.streamlit.app/

---

## 🌍 Project Overview

Pila has ~57,776 residents across 17 barangays.  
In real life, lost pets are often recovered through community visibility, especially Facebook groups, neighbors, and barangay coordination.

This app helps pet owners:

- Understand recovery likelihood early
- Take effective actions (posting on Facebook, searching nearby areas)
- Stay guided and encouraged during stressful situations

---

## 🔢 Model Versions Summary

| Version | Accuracy | Recall (Found) | Notes |
|--------|---------|----------------|------|
| v3     | 75.2%   | 83.2%          | Some false negatives |
| v4     | 100%    | 100%           | Added days_missing_bucket, logging, helper scripts |
| v5     | Public-focused | High recall | Image embeddings, similarity metrics, public explanations |

⚠️ **Important:** Metrics are based on synthetic / limited data. Real-world data collection is ongoing.

---

## 🧠 Core Prediction Model (v5)

**Model Type:** RandomForestClassifier  
**Input Type:** Tabular data (6 features)

### Features Used

- Pet age (years)  
- Days missing  
- `days_missing_bucket` (engineered feature)  
- Barangay (label-encoded)  
- Near Laguna de Bay / water area  
- Posted on Facebook or local groups (**strongest predictor**)

---

## 🧩 Why Pet Name Is Not Required for Prediction

The AI model does **not** require a pet name to generate predictions.  
This is intentional and follows machine learning best practices:

- The model predicts **outcomes**, not identities  
- Pet names are **non-causal identifiers** (e.g., “Ginger”, “Ming-ming”)  
- Names provide no statistical signal for recovery likelihood  
- Including names would add noise and reduce generalization  

### Where pet names *are* used

Pet names are optional metadata and are only used for:

- Image-to-record association  
- Human-readable logs and dashboards  
- Migration and admin tooling

---

## Why Pet Type Is Not Used

Pet type was intentionally removed to make the model:

- Universal (dogs, cats, birds, rabbits, etc.)  
- Less biased by assumptions  
- More robust with small datasets

---

## days_missing_bucket (Key Innovation)

Instead of relying on raw days alone, days missing are bucketed:

| Bucket | Days Missing |
|--------|-------------|
| 0      | 1–3 days    |
| 1      | 4–7 days    |
| 2      | 8–14 days   |
| 3      | 15+ days    |

This captures non-linear recovery behavior and significantly improves recall.

---

## 🖼️ Image Uploads & Embeddings (v5)

**What happens when users upload images?**

1. Images are saved to disk (`/uploads`)  
2. A **512-dimensional color histogram embedding** is computed  
3. Embeddings are stored in PostgreSQL (`pet_images.embedding`)  
4. Images are safely archived in `uploads/processed/`  
5. Embeddings are used for similarity scoring, not prediction (yet)

---

## 🔍 Image Similarity (v5)

- Cosine similarity is computed between uploaded images and existing pet images  
- The maximum similarity score is exposed internally  
- Used for:
  - Explaining confidence  
  - Future matching / “similar-looking pet” features  

⚠️ **Image embeddings do NOT directly affect the RandomForest prediction.**

This separation ensures:

- Model stability  
- Explainability  
- Future-proof architecture

---

## 🧪 Embedding Method (Python 3.12 Safe)

- No TensorFlow / PyTorch required  
- No GPU required  
- Deterministic & fast  
- Explainable (RGB histogram)

Current method can later be swapped with:

- CLIP  
- MobileNet / EfficientNet  
- Custom CNN  

> No database changes required.

---

## 🧰 Embedding Migration Scripts

To support legacy data, v5 introduces migration utilities:

- **migrate_csv_to_db.py**  
  Imports historical CSV data into PostgreSQL  

- **migrate_embeddings_flexible.py**    
  Matches images to pets by name  
  Auto-fills missing `pet_name` values (`Pet-<id>`)  
  Computes embeddings  
  Prevents duplicate processing  
  Safe to rerun (idempotent)

---

📋 Database Schema Reference

For developer reference, see `core/db/schemas.py` for detailed table and field documentation:

- `lost_pets` — stores pet metadata
- `pet_images` — stores uploaded images and embeddings
- `predictions` — stores model prediction results

This file includes notes on required vs optional fields and explains which fields are used by the v5 model.

---

## 🧱 System Architecture

**Streamlit UI**  
↓  
App Controller  
↓  
RandomForest (tabular prediction)  
↓  
Probability + Public-Friendly Advice  

**Images**  
↓  
Embeddings (stored in DB)  
↓  
Similarity scoring (v5)  
↓  
Future vision models

---

## 🛠️ Tech Stack

- Python 3.12  
- Streamlit  
- Scikit-learn  
- PostgreSQL  
- SQLAlchemy  
- Pillow  
- NumPy  
- Joblib

---

## ▶️ Running Locally

1. **Clone the repository**

```bash
git clone https://github.com/your-username/lost-pet-ai.git
cd lost-pet-ai

2. Clone the repository

pip install -r requirements.txt

3. Ensure model files exist

pkl/
├─ lost_pet_model_v5.pkl
├─ le_barangay.pkl

4. Run the app

streamlit run app.py

🧪 Testing Without Streamlit
python -m core.predict

Returns:

pet_id
pet_name
probability
days_bucket
embeddings_count
max_similarity
result_text

📊 Admin Dashboard

Admin-only features include:

Prediction history
Barangay trends
Recovery statistics
Image similarity inspection

⚠️ Dashboard data represents training / demo data only.

🚀 Future Roadmap
🔍 Visual similarity search (find matching pets)
🧠 Hybrid tabular + vision models
⚡ FAISS vector indexing
📊 Real community & Facebook signal ingestion
🌐 Expansion beyond Pila, Laguna

🤝 Contributing

Pull requests are welcome.

Please:

❌ Do not commit large .pkl files
🔒 Respect data privacy
🚫 Avoid uploading real owner-identifying data