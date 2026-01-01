# core/db/db_utils.py
from sqlalchemy import text
from .db import SessionLocal
import json

def log_prediction(lost_pet_id: int, predicted_status: str, probability: float, days_bucket: int):
    """Logs a prediction into the predictions table."""
    session = SessionLocal()
    try:
        query = """
            INSERT INTO predictions (
                lost_pet_id,
                predicted_status,
                probability,
                days_missing_bucket
            ) VALUES (
                :lost_pet_id,
                :predicted_status,
                :probability,
                :days_bucket
            )
        """
        session.execute(
            text(query),
            {
                "lost_pet_id": lost_pet_id,
                "predicted_status": predicted_status,
                "probability": probability,
                "days_bucket": days_bucket
            }
        )
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def insert_pet_embedding(lost_pet_id: int, image_path: str, embedding: list):
    """Inserts a pet image embedding into the pet_images table."""
    session = SessionLocal()
    try:
        query = """
            INSERT INTO pet_images (lost_pet_id, image_path, embedding)
            VALUES (:lost_pet_id, :image_path, :embedding)
        """
        session.execute(
            text(query),
            {
                "lost_pet_id": lost_pet_id,
                "image_path": image_path,
                "embedding": json.dumps(embedding)
            }
        )
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()