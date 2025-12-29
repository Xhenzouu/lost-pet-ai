# scripts/migrate_embeddings.py
import sys
from pathlib import Path

# 🔹 Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.models.lost_pet_model import LostPetModel
from core.db.db import SessionLocal
from sqlalchemy import text

# Directory where uploaded images are stored
UPLOADS_DIR = BASE_DIR / "uploads"
PLACEHOLDER_IMAGE = UPLOADS_DIR / "placeholder.png"

def migrate_embeddings():
    session = SessionLocal()
    try:
        # Fetch all lost pets with ID and name
        lost_pets = session.execute(text("SELECT id, pet_name FROM lost_pets")).fetchall()
        print(f"Found {len(lost_pets)} lost pets in DB")

        for lp in lost_pets:
            lost_pet_id = lp.id
            pet_name = (lp.pet_name or "").strip().lower()
            if not pet_name:
                print(f"Skipped lost_pet_id {lost_pet_id} — no pet name")
                continue

            # Skip if embeddings already exist
            existing = session.execute(
                text("SELECT COUNT(*) FROM pet_images WHERE lost_pet_id = :lp_id"),
                {"lp_id": lost_pet_id}
            ).scalar()
            if existing:
                print(f"Skipped lost_pet_id {lost_pet_id} — embeddings already exist")
                continue

            # -------------------------------
            # Find images with exact pet_name (ignore extension)
            # -------------------------------
            matched_files = [
                f for f in UPLOADS_DIR.iterdir()
                if f.is_file() and f.stem.lower() == pet_name
            ]

            # Fallback to placeholder if no image found
            if not matched_files:
                if PLACEHOLDER_IMAGE.exists():
                    print(f"No image found for '{pet_name}', using placeholder")
                    matched_files = [PLACEHOLDER_IMAGE]
                else:
                    print(f"No image or placeholder found for '{pet_name}', skipping")
                    continue

            embeddings = []
            for file_path in matched_files:
                try:
                    with open(file_path, "rb") as f:
                        # Mock UploadedFile like Streamlit
                        uploaded_file = type(
                            'UploadedFile',
                            (object,),
                            {"name": file_path.name, "getbuffer": lambda f=f: f.read()}
                        )()
                        emb = LostPetModel.save_pet_image_with_embedding(lost_pet_id, uploaded_file)
                        embeddings.append(emb)
                except Exception as e:
                    print(f"Failed to process {file_path.name}: {e}")

            print(f"Processed lost_pet_id {lost_pet_id} ({pet_name}), {len(embeddings)} embeddings created")

        session.commit()
        print("✅ Embedding migration complete")

    except Exception as e:
        session.rollback()
        print("❌ Migration failed:", e)

    finally:
        session.close()

if __name__ == "__main__":
    migrate_embeddings()