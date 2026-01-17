# core/controllers/found_pet_controller.py
from core.models.lost_pet_model import LostPetModel, compute_embedding_from_upload
from core.db.db import SessionLocal
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

class FoundPetController:
    def __init__(self):
        pass

    def handle_found_pet_submission(self, uploaded_files, barangay):
        """
        Process found pet photos, compute embeddings, search for matches.
        Returns dict with matches including details and all images.
        """
        if not uploaded_files:
            return {"error": "No photos uploaded."}

        embeddings = []
        for file in uploaded_files:
            emb = compute_embedding_from_upload(file)
            if emb:
                embeddings.append(emb)

        if not embeddings:
            return {"error": "Couldn't process any photos. Try clearer images."}

        # Use first embedding for MVP search
        query_emb = embeddings[0]
        try:
            LostPetModel._load_faiss_index()
            scores, indices = LostPetModel.compute_similarity(query_emb, k=5)

            matches = []
            session = SessionLocal()
            try:
                for score, idx in zip(scores, indices):
                    if idx == -1:
                        continue

                    # Fetch lost pet details + ALL images
                    query = text("""
                        SELECT 
                            lp.pet_type, lp.age_years, lp.days_missing, lp.barangay,
                            pi.image_path
                        FROM lost_pets lp
                        INNER JOIN pet_images pi ON pi.lost_pet_id = lp.id
                        WHERE lp.id = :lost_id
                    """).bindparams(lost_id=idx)

                    rows = session.execute(query).fetchall()

                    if rows:
                        # Basic info from first row
                        pet_type = rows[0][0] or 'Unknown'
                        age = rows[0][1] or 'Unknown'
                        days_missing = rows[0][2]
                        barangay = rows[0][3]

                        # Collect all image URLs
                        image_paths = [row[4] for row in rows if row[4]]

                        matches.append({
                            "lost_pet_id": idx,
                            "similarity": round(score, 3),
                            "pet_type": pet_type,
                            "age": age,
                            "days_missing": days_missing,
                            "barangay": barangay,
                            "image_paths": image_paths  # List of all photos
                        })

            finally:
                session.close()

            return {
                "matches": matches,
                "barangay": barangay,
                "num_photos": len(uploaded_files)
            }

        except Exception as e:
            logger.error(f"FAISS or DB search failed: {e}")
            return {"error": "Failed to search for matches. Please try again."}