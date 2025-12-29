# core/db/db.py

from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import sessionmaker
import json
import logging
from ..config import DB_URL

# -------------------------------
# Configure logging
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("db.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# -------------------------------
# Engine & Session
# -------------------------------
engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(bind=engine, future=True)

# -------------------------------
# Metadata
# -------------------------------
metadata = MetaData()

# -------------------------------
# Reflect tables
# -------------------------------
lost_pets_table = Table("lost_pets", metadata, autoload_with=engine)
pet_images_table = Table("pet_images", metadata, autoload_with=engine)

# -------------------------------
# Fetch lost pet record
# -------------------------------
def get_lost_pet(pet_id: int):
    session = SessionLocal()
    try:
        stmt = select(
            lost_pets_table.c.id,
            lost_pets_table.c.pet_name,
            lost_pets_table.c.pet_type,
            lost_pets_table.c.age_years,
            lost_pets_table.c.days_missing,
            lost_pets_table.c.near_water,
            lost_pets_table.c.posted_on_fb,
            lost_pets_table.c.barangay
        ).where(lost_pets_table.c.id == pet_id)
        pet_row = session.execute(stmt).first()
        if not pet_row:
            logging.warning(f"Pet ID {pet_id} not found in DB.")
            return None

        pet_data = dict(pet_row._mapping)
        pet_data["age"] = float(pet_data.pop("age_years"))
        pet_data["embeddings"] = []

        stmt_images = select(pet_images_table.c.embedding).where(
            pet_images_table.c.lost_pet_id == pet_id
        )
        image_rows = session.execute(stmt_images).all()
        embeddings = []
        for r in image_rows:
            if r[0]:
                embeddings.append(json.loads(r[0]))
        pet_data["embeddings"] = embeddings

        logging.info(f"Fetched pet ID {pet_id} with {len(embeddings)} embeddings.")
        return pet_data
    except Exception as e:
        logging.error(f"Failed to fetch pet ID {pet_id}: {str(e)}")
        return None
    finally:
        session.close()