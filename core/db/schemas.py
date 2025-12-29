# core/db/schemas.py
"""
Schema reference for Lost Pet Reunion AI – Pila, Laguna

This file provides a clear reference for all tables and their fields.
It is intended for documentation and developer reference only.
Does NOT modify the database.
"""

# -------------------------------
# Lost Pets Table
# -------------------------------
lost_pets_fields = {
    "id": "integer, primary key, auto-increment",
    "pet_name": "text, optional — used for image association and logging",
    "pet_type": "text, optional — not used in prediction",
    "age_years": "numeric(4,2), required — used in prediction",
    "days_missing": "integer, required — used in prediction",
    "near_water": "boolean, required — used in prediction",
    "posted_on_fb": "boolean, required — used in prediction",
    "barangay": "text, required — used in prediction (label-encoded)",
    "found": "boolean, default false — indicates if pet is recovered",
    "reported_at": "timestamp, default CURRENT_TIMESTAMP",
    "found_at": "timestamp, optional"
}

# -------------------------------
# Pet Images Table
# -------------------------------
pet_images_fields = {
    "id": "integer, primary key, auto-increment",
    "lost_pet_id": "integer, foreign key → lost_pets(id), required",
    "image_path": "text, required — path to image file",
    "embedding": "jsonb, optional — 512-dim color histogram or future embedding",
    "uploaded_at": "timestamp, default CURRENT_TIMESTAMP"
}

# -------------------------------
# Predictions Table
# -------------------------------
predictions_fields = {
    "id": "integer, primary key, auto-increment",
    "lost_pet_id": "integer, foreign key → lost_pets(id), optional (null if no match)",
    "predicted_status": "text, required — e.g., Likely Found / Unlikely Found",
    "probability": "double precision, required — probability of being found",
    "days_missing_bucket": "integer, required — engineered feature from days_missing",
    "predicted_at": "timestamp, default CURRENT_TIMESTAMP"
}

# -------------------------------
# Notes
# -------------------------------
notes = """
- pet_name is optional for prediction but used for image association, logging, and admin dashboards.
- pet_type is not used in v5 prediction.
- Embeddings in pet_images are stored for similarity search / future models; they do not affect current tabular RandomForest predictions.
- The fields above match the database schema but do not enforce types; actual DB constraints are in PostgreSQL.
"""