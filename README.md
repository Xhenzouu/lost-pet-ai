# Lost Pet Reunion AI – Pila, Laguna 🐕🐈🐇🐦🐢

A machine learning–powered community project that predicts the likelihood of a lost pet being reunited with its owner in **Pila, Laguna, Philippines**.

Designed for real-world public use, this system prioritizes:

- 🧠 High recall (don’t miss pets that are likely to be found)
- 👥 Simplicity and clarity for non-technical users
- 🔮 Extensibility for future AI upgrades (vision + similarity search)

**Current production version:** v6 (Deep Vision Upgrade – Jan 2026)

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

| Version | Status                  | Key Features & Notes |
|---------|-------------------------|----------------------|
| v3      | Legacy                  | Initial RandomForest, some false negatives |
| v4      | Legacy                  | Added days_missing_bucket, logging, helpers |
| v5      | Public Release          | Color histogram embeddings (512-dim), public explanations |
| **v6**  | **Current – Deep Vision** | **YOLO11** pet detection + cropping + **DINOv2-small** embeddings (384-dim), FAISS cosine similarity, migration scripts |

⚠️ **Important:** Metrics are based on synthetic / limited data. Real-world data collection is ongoing.

---

## 🧠 Core Prediction Model (v6)

**Model Type:** RandomForestClassifier  
**Input Type:** Tabular data (6 features) + optional image similarity signals

### Features Used

- Pet age (years)  
- Days missing  
- `days_missing_bucket` (engineered feature)  
- Barangay (label-encoded)  
- Near Laguna de Bay / water area  
- Posted on Facebook or local groups (**strongest predictor**)

Image similarity now feeds into future hybrid models (not yet affecting tabular prediction directly).

---

## 🖼️ Image Uploads & Embeddings (v6 – Major Upgrade)

**What happens when users upload images?**

1. Images uploaded via Streamlit  
2. **YOLO11n** (Ultralytics) detects & crops pet (cat/dog classes, fallback to full image)  
3. **DINOv2-small** (facebook/dinov2-small) computes **384-dimensional** normalized embedding (CLS token)  
4. Original image uploaded to Cloudinary  
5. New embedding stored in PostgreSQL (`pet_images.embedding` as JSONB)  
6. Embeddings used for cosine similarity search via **FAISS** (`IndexFlatIP`)

**Migration completed:** 10/14 legacy images upgraded from old 512-dim histograms to new 384-dim DINOv2 (Jan 10, 2026)

---

## 🔍 Image Similarity (v6)

- Cosine similarity computed between new/found pet images and existing lost pets  
- Top-k matches returned (currently internal, ready for "Found Pet" feature)  
- Uses normalized vectors + **IndexFlatIP** for fast, accurate search

**Image embeddings do NOT yet affect the RandomForest prediction** (kept separate for stability/explainability).

---

## 🧪 Embedding Method (Python 3.12/3.13 Safe)

- **Detection:** Ultralytics YOLO11n (lightweight, CPU-friendly)  
- **Embedding:** Hugging Face DINOv2-small (no GPU required for inference)  
- Deterministic, normalized outputs  
- Explainable fallback to full image if no pet detected

---

## 🧰 Embedding Migration Scripts

To support legacy data during the v5 → v6 transition:

- **migrate_embeddings_to_dinov2.py**  
  One-time script: Recomputes all embeddings using YOLO11 + DINOv2-small  
  (Completed Jan 10, 2026: 10/14 images upgraded)

Other utilities:
- **migrate_csv_to_db.py** — Historical CSV import
- **migrate_embeddings_flexible.py** — Legacy name-based matching

---

📋 Database Schema Reference

See `core/db/schemas.py` for details:

- `lost_pets` — pet metadata
- `pet_images` — images + 384-dim embeddings (JSONB)
- `predictions` — model outputs

---

## 🧱 System Architecture

**Streamlit UI**  
↓  
App Controller  
↓  
RandomForest (tabular prediction) + Probability Advice  

**Images**  
↓  
YOLO11 detection → crop → DINOv2 embedding  
↓  
FAISS vector index → cosine similarity search  
↓  
Future: "Found Pet" matching alerts

---

## 🛠️ Tech Stack (Updated Jan 2026)

- Python 3.12 / 3.13  
- Streamlit  
- Scikit-learn + Joblib  
- PostgreSQL + SQLAlchemy + psycopg2  
- **Ultralytics YOLO11** (pet detection)  
- **Hugging Face Transformers** + **Torch** (DINOv2 embeddings)  
- **FAISS** (vector similarity)  
- Pillow + NumPy  
- Cloudinary (image storage)

---

## ☁️ Cloud Database

Hosted on **Railway**.  
Credentials via Streamlit secrets.  
No local DB needed for running.

---

## ▶️ Running Locally

1. Clone repo  
2. `cd lost-pet-ai`  
3. Activate venv: `.\venv\Scripts\activate` (Windows)  
4. `pip install -r requirements.txt`  
5. Ensure pkl files exist  
6. `streamlit run app.py`

---

## 🚀 Future Roadmap

- ✅ **Deep visual embeddings** (DINOv2-small + YOLO11 detection)  
- ✅ **FAISS cosine similarity** (384-dim index)  
- 🔜 **Found Pet Report** page → upload photo → show matching lost pets  
- 🔜 Hybrid model (tabular + vision similarity features)  
- 🔜 Real-time alerts (email/Telegram for high-similarity matches)  
- 🔜 Real community & Facebook signal ingestion  
- 🌐 Expansion beyond Pila, Laguna

🤝 Contributing

Pull requests welcome!

Please:
- ❌ Do not commit large .pkl files  
- 🔒 Respect data privacy  
- 🚫 Avoid real owner-identifying data