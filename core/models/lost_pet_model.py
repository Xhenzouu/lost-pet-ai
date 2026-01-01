# core/models/lost_pet_model.py
from sqlalchemy import text
from core.db.db import SessionLocal
from typing import List
import json
import numpy as np
from PIL import Image
import io
import cloudinary
import cloudinary.uploader

def compute_color_histogram_embedding(img: Image.Image) -> List[float]:
    img = img.resize((224, 224)).convert("RGB")
    img_array = np.array(img)
    hist = np.histogramdd(
        img_array.reshape(-1, 3),
        bins=(8, 8, 8),
        range=((0, 256), (0, 256), (0, 256))
    )[0]
    return (hist.flatten() / (np.linalg.norm(hist.flatten()) + 1e-8)).tolist()

class LostPetModel:
    @staticmethod
    def save_lost_pet(pet_type, age_years, days_missing, near_water, posted_on_fb, barangay) -> int:
        session = SessionLocal()
        lost_pet_id = None
        try:
            query = """
                INSERT INTO lost_pets (
                    pet_type, age_years, days_missing, near_water, posted_on_fb, barangay
                ) VALUES (
                    :pet_type, :age_years, :days_missing, :near_water, :posted_on_fb, :barangay
                ) RETURNING id
            """
            result = session.execute(text(query), {
                "pet_type": pet_type,
                "age_years": age_years,
                "days_missing": days_missing,
                "near_water": near_water,
                "posted_on_fb": posted_on_fb,
                "barangay": barangay
            })
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
        embeddings = []
        if not uploaded_files:
            return embeddings

        for file in uploaded_files:
            emb = LostPetModel.save_pet_image_with_embedding(lost_pet_id, file)
            if emb:
                embeddings.append(emb)
        return embeddings

    @staticmethod
    def save_pet_image_with_embedding(lost_pet_id: int, uploaded_file) -> List[float]:
        session = SessionLocal()
        embedding = None
        try:
            if hasattr(uploaded_file, "getbuffer"):
                file_bytes = uploaded_file.getbuffer()
            else:
                uploaded_file.seek(0)
                file_bytes = uploaded_file.read()
                uploaded_file.seek(0)

            upload_result = cloudinary.uploader.upload(
                io.BytesIO(file_bytes),
                folder="pila_pets_ai",
                resource_type="image"
            )
            image_url = upload_result.get("secure_url")
            img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
            embedding = compute_color_histogram_embedding(img)

            query = """
                INSERT INTO pet_images (lost_pet_id, image_path, embedding)
                VALUES (:lost_pet_id, :image_path, :embedding)
            """
            session.execute(text(query), {
                "lost_pet_id": lost_pet_id,
                "image_path": image_url,
                "embedding": json.dumps(embedding)
            })
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
        return embedding

    @staticmethod
    def get_existing_embeddings() -> List[List[float]]:
        session = SessionLocal()
        embeddings_list = []
        try:
            rows = session.execute(text("SELECT embedding FROM pet_images")).fetchall()
            for r in rows:
                if r.embedding:
                    embeddings_list.append(json.loads(r.embedding))
        finally:
            session.close()
        return embeddings_list