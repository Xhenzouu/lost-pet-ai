# migrate_embeddings_to_dinov2.py
"""
One-time migration: Recompute all pet_images embeddings using YOLO11 crop + DINOv2-small (384-dim)

You can run this from inside the scripts/ folder:
python migrate_embeddings_to_dinov2.py
"""

import sys
import os

# ── Make sure we can import from project root ──
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import time
from pathlib import Path
import json
from typing import Optional

import numpy as np
from PIL import Image
import io
import requests
import logging
from sqlalchemy import text
from tqdm import tqdm

# Project imports
from core.db.db import SessionLocal
from core.models.lost_pet_model import (
    detect_and_crop_pet,
    compute_dinov2_embedding,
    EMBEDDING_DIM
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BATCH_SIZE = 10          # Process this many images per transaction
SLEEP_BETWEEN_BATCHES = 1  # seconds - gentle on resources

def download_image_from_url(url: str) -> Optional[bytes]:
    """Download image bytes from Cloudinary URL"""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logger.warning(f"Failed to download {url}: {e}")
        return None

def migrate_all_embeddings():
    session = SessionLocal()
    try:
        # Get all pet_images rows
        query = text("""
            SELECT id, image_path, embedding
            FROM pet_images
            ORDER BY id
        """)
        rows = session.execute(query).fetchall()

        total = len(rows)
        if total == 0:
            print("No images found in pet_images table. Nothing to migrate.")
            return

        print(f"Found {total} images to migrate to DINOv2-small (384-dim)...")
        print(f"Current EMBEDDING_DIM = {EMBEDDING_DIM}")

        updated_count = 0
        skipped_count = 0

        # Process in batches
        for i in tqdm(range(0, total, BATCH_SIZE), desc="Migrating", unit="batch"):
            batch = rows[i:i + BATCH_SIZE]

            for row in batch:
                row_id, image_url, old_emb = row

                file_bytes = download_image_from_url(image_url)
                if not file_bytes:
                    skipped_count += 1
                    continue

                # Process with current pipeline
                cropped = detect_and_crop_pet(file_bytes)
                if cropped is None:
                    logger.info(f"No pet detected in id={row_id} → using full image")
                    try:
                        cropped = Image.open(io.BytesIO(file_bytes)).convert("RGB")
                    except Exception:
                        skipped_count += 1
                        continue

                new_embedding = compute_dinov2_embedding(cropped)

                if new_embedding is None or len(new_embedding) != EMBEDDING_DIM:
                    logger.warning(f"Failed to compute new embedding for id={row_id}")
                    skipped_count += 1
                    continue

                # Convert to JSON string for jsonb column
                embedding_json = json.dumps(new_embedding)

                # Update the row
                update_query = text("""
                    UPDATE pet_images
                    SET embedding = :new_embedding
                    WHERE id = :id
                """)
                session.execute(update_query, {
                    "new_embedding": embedding_json,
                    "id": row_id
                })

                updated_count += 1

            session.commit()  # Commit batch
            logger.info(f"Batch committed: {updated_count} updated / {skipped_count} skipped so far")
            time.sleep(SLEEP_BETWEEN_BATCHES)

        print("\nMigration finished!")
        print(f"Successfully updated: {updated_count}")
        print(f"Skipped/failed: {skipped_count}")
        print(f"Total processed: {updated_count + skipped_count} / {total}")

    except Exception as e:
        session.rollback()
        logger.error(f"Migration failed: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("Starting DINOv2-small embedding migration...")
    print("Make sure you have backed up your database!")
    input("Press Enter to continue (Ctrl+C to cancel)...\n")

    migrate_all_embeddings()

    print("\nNext steps:")
    print("1. Restart your Streamlit app")
    print("2. The FAISS index will auto-rebuild with 384-dim vectors when needed")
    print("3. Test by submitting new lost pet reports")