# scripts/insert_test_image_embedding.py

import sys
from pathlib import Path
import json
import logging

# -------------------------------------------------
# Ensure project root is importable (works from venv)
# -------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# -----------------------------
# Imports from your project
# -----------------------------
from core.db.db import SessionLocal, pet_images_table
from core.embeddings import generate_image_embedding  # <-- corrected

# -----------------------------
# CONFIG
# -----------------------------
LOST_PET_ID = 1
IMAGE_PATH = Path(
    r"C:\Users\arroy\lost-pet-ai\uploads\processed\383b9a6c049c389fde58a08e8cf18f30.jpg"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# -----------------------------
# MAIN SCRIPT
# -----------------------------
def main():
    if SessionLocal is None or pet_images_table is None:
        logging.error("❌ Database not initialized.")
        return

    if not IMAGE_PATH.exists():
        logging.error(f"❌ Image not found: {IMAGE_PATH}")
        return

    logging.info("📸 Loading image and generating embedding...")
    embedding = generate_image_embedding(str(IMAGE_PATH))

    if not embedding:
        logging.error("❌ Failed to generate embedding.")
        return

    session = SessionLocal()
    try:
        stmt = pet_images_table.insert().values(
            lost_pet_id=LOST_PET_ID,
            image_path=str(IMAGE_PATH),
            embedding=json.dumps(embedding)
        )
        session.execute(stmt)
        session.commit()

        logging.info(
            f"✅ Inserted image embedding for pet ID {LOST_PET_ID} "
            f"(dim={len(embedding)})"
        )

    except Exception as e:
        session.rollback()
        logging.error(f"❌ Failed to insert embedding: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    main()