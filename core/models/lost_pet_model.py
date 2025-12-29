# core/models/lost_pet_model.py

from sqlalchemy import text
from core.db.db import SessionLocal
from pathlib import Path
from typing import List
import json
import numpy as np
from PIL import Image

# =====================================================
# IMAGE EMBEDDING STRATEGY (COLOR HISTOGRAM)
# -----------------------------------------------------
# - Fast, deterministic, Python 3.12 safe
# - 512-dimensional normalized vector
# - Ideal for similarity search
# =====================================================

def compute_color_histogram_embedding(img: Image.Image) -> List[float]:
    """
    Compute a simple RGB histogram embedding.
    Args:
        img: PIL.Image object
    Returns:
        512-dim normalized histogram as list[float]
    """
    img = img.resize((224, 224)).convert("RGB")
    img_array = np.array(img)

    # 8 bins per channel → 8 x 8 x 8 = 512 features
    hist = np.histogramdd(
        img_array.reshape(-1, 3),
        bins=(8, 8, 8),
        range=((0, 256), (0, 256), (0, 256))
    )[0]

    # Normalize to unit vector
    hist_flat = hist.flatten()
    hist_norm = hist_flat / (np.linalg.norm(hist_flat) + 1e-8)

    return hist_norm.tolist()


# =====================================================
# LOST PET MODEL CLASS
# =====================================================

class LostPetModel:

    @staticmethod
    def save_lost_pet(
        pet_type: str,
        age_years: float,
        days_missing: int,
        near_water: bool,
        posted_on_fb: bool,
        barangay: str
    ) -> int:
        """
        Save lost pet metadata and return its database ID.
        """
        session = SessionLocal()
        lost_pet_id = None

        try:
            query = """
                INSERT INTO lost_pets (
                    pet_type,
                    age_years,
                    days_missing,
                    near_water,
                    posted_on_fb,
                    barangay
                )
                VALUES (
                    :pet_type,
                    :age_years,
                    :days_missing,
                    :near_water,
                    :posted_on_fb,
                    :barangay
                )
                RETURNING id
            """
            result = session.execute(
                text(query),
                {
                    "pet_type": pet_type,
                    "age_years": age_years,
                    "days_missing": days_missing,
                    "near_water": near_water,
                    "posted_on_fb": posted_on_fb,
                    "barangay": barangay
                }
            )
            lost_pet_id = result.scalar()
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

        return lost_pet_id

    @staticmethod
    def save_pet_images(lost_pet_id: int, uploaded_files: list) -> List[List[float]]:
        """
        Save multiple images and compute embeddings.
        Returns list of embeddings.
        """
        if not uploaded_files:
            return []

        embeddings = []
        for file in uploaded_files:
            emb = LostPetModel.save_pet_image_with_embedding(lost_pet_id, file)
            if emb:
                embeddings.append(emb)

        return embeddings

    @staticmethod
    def save_pet_image_with_embedding(lost_pet_id: int, uploaded_file) -> List[float]:
        """
        Save a single uploaded image and compute its embedding.
        Embedding is stored as JSON in pet_images table.
        """
        session = SessionLocal()
        embedding = None

        try:
            # Ensure uploads directory
            uploads_dir = Path("uploads")
            uploads_dir.mkdir(exist_ok=True)

            save_path = uploads_dir / uploaded_file.name

            # Save uploaded file
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Load image
            img = Image.open(save_path).convert("RGB")

            # Compute embedding
            embedding = compute_color_histogram_embedding(img)

            # Insert into DB
            query = """
                INSERT INTO pet_images (
                    lost_pet_id,
                    image_path,
                    embedding
                )
                VALUES (
                    :lost_pet_id,
                    :image_path,
                    :embedding
                )
            """
            session.execute(
                text(query),
                {
                    "lost_pet_id": lost_pet_id,
                    "image_path": str(save_path),
                    "embedding": json.dumps(embedding)
                }
            )
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

        return embedding

    @staticmethod
    def get_existing_embeddings() -> List[List[float]]:
        """
        Fetch all embeddings from previously found pets.
        Returns list of 512-dim embeddings.
        """
        session = SessionLocal()
        embeddings_list = []

        try:
            query = "SELECT embedding FROM pet_images"
            rows = session.execute(text(query)).fetchall()
            for row in rows:
                if row.embedding:
                    embeddings_list.append(json.loads(row.embedding))
        finally:
            session.close()

        return embeddings_list