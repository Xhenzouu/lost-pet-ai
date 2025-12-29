# scripts/migrate_embeddings_idempotent.py

import sys
from pathlib import Path
from PIL import Image
import json
import numpy as np
import re
import shutil

# 🔹 Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.db.db import SessionLocal
from core.models.lost_pet_model import compute_color_histogram_embedding
from sqlalchemy import text

# -------------------------------
# Uploads directory
# -------------------------------
UPLOADS_DIR = BASE_DIR / "uploads"
PROCESSED_DIR = UPLOADS_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)

def normalize_name(name: str) -> str:
    """Normalize a name for flexible image matching."""
    name = name.lower()
    name = re.sub(r'[\s_]+', '-', name)
    name = re.sub(r'[^a-z0-9\-]', '', name)
    return name

def migrate_embeddings():
    session = SessionLocal()
    migrated_count = 0
    skipped = []

    try:
        # Fetch all lost_pets
        pets = session.execute(text("SELECT id, pet_name FROM lost_pets")).mappings().all()

        # Get existing images already in pet_images table
        existing_images = session.execute(text("SELECT image_path FROM pet_images")).scalars().all()
        existing_images_set = set(existing_images)

        # Gather all image files in uploads
        image_files = list(UPLOADS_DIR.glob("*.jpg"))

        for pet in pets:
            lost_pet_id = pet["id"]
            pet_name = pet["pet_name"]

            # Auto-fill missing pet names
            if not pet_name or not pet_name.strip():
                pet_name = f"Pet-{lost_pet_id}"
                session.execute(
                    text("UPDATE lost_pets SET pet_name = :pet_name WHERE id = :id"),
                    {"pet_name": pet_name, "id": lost_pet_id}
                )
                print(f"📝 Auto-filled lost_pet_id {lost_pet_id} — pet_name set to '{pet_name}'")

            normalized_name = normalize_name(pet_name)

            # Find all matching images (starts with pet_name)
            matching_images = [f for f in image_files if normalize_name(f.stem).startswith(normalized_name)]

            if not matching_images:
                skipped.append((lost_pet_id, f"no matching image for '{pet_name}'"))
                continue

            for idx, image_file in enumerate(matching_images, start=1):
                # Skip if image already processed
                if str(PROCESSED_DIR / f"{pet_name}_{idx}.jpg") in existing_images_set:
                    skipped.append((lost_pet_id, f"image '{image_file.name}' already processed"))
                    continue

                # Load image and compute embedding
                img = Image.open(image_file).convert("RGB")
                embedding = compute_color_histogram_embedding(img)

                # Rename to unique image path: petname_1.jpg, petname_2.jpg, etc.
                unique_image_name = f"{pet_name}_{idx}.jpg"
                unique_image_path = PROCESSED_DIR / unique_image_name

                # Move image to processed folder
                shutil.move(str(image_file), unique_image_path)

                # Insert into pet_images table
                session.execute(
                    text("""
                        INSERT INTO pet_images (lost_pet_id, image_path, embedding)
                        VALUES (:lost_pet_id, :image_path, :embedding)
                    """),
                    {
                        "lost_pet_id": lost_pet_id,
                        "image_path": str(unique_image_path),
                        "embedding": json.dumps(embedding)
                    }
                )
                migrated_count += 1

        session.commit()

        # Summary
        for s in skipped:
            print(f"⚠️ Skipped lost_pet_id {s[0]} — {s[1]}")
        print(f"✅ Embedding migration complete — {migrated_count} images processed")
        print(f"📂 Processed images stored in '{PROCESSED_DIR}'")

    except Exception as e:
        session.rollback()
        print("❌ Migration failed:", e)

    finally:
        session.close()


if __name__ == "__main__":
    migrate_embeddings()