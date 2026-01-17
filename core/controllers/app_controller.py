from core.models.lost_pet_model import LostPetModel
from core.model import load_model_artifacts, predict_reunion, bucket_days
from core.db.db_utils import log_prediction
from core.views.dashboard_view import DashboardView
from core.public_helpers import interpret_prediction

class AppController:
    MIN_PUBLIC_PROB = 0.05

    def __init__(self):
        self.model, self.le_barangay = load_model_artifacts(v5=True)
        self.dashboard_view = DashboardView()

    def to_bool(self, value):
        """Convert various inputs to boolean safely."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ("yes", "true", "1", "y")
        if isinstance(value, (int, float)):
            return bool(value)
        return False

    def handle_submission(self, pet_type, age, days, barangay, near_water, posted_on_fb, uploaded_files):
        near_water_bool = self.to_bool(near_water)
        posted_on_fb_bool = self.to_bool(posted_on_fb)

        lost_pet_id = LostPetModel.save_lost_pet(
            pet_type=pet_type,
            age_years=age,
            days_missing=days,
            near_water=near_water_bool,
            posted_on_fb=posted_on_fb_bool,
            barangay=barangay
        )
        if not lost_pet_id:
            return {"error": "Failed to save lost pet to database."}

        embeddings = LostPetModel.save_pet_images(lost_pet_id, uploaded_files)

        similar_pets = []
        if embeddings:
            try:
                LostPetModel._load_faiss_index()

                query_emb = embeddings[-1]
                scores, indices = LostPetModel.compute_similarity(query_emb, k=3)

                similar_pets = [
                    {"index": idx, "similarity": round(score, 3)}
                    for score, idx in zip(scores, indices)
                    if idx != -1
                ]
            except Exception as faiss_err:
                print(f"FAISS similarity search failed: {faiss_err}")
                similar_pets = []

        try:
            raw_prediction = predict_reunion(
                model=self.model,
                le_barangay=self.le_barangay,
                age=age,
                days_missing=days,
                barangay_input=barangay,
                near_water=near_water_bool,
                posted_on_fb=posted_on_fb_bool,
                embeddings=embeddings
            )
        except Exception as pred_err:
            print(f"Prediction failed: {pred_err}")
            raw_prediction = {
                "result_text": "Prediction failed",
                "probability": 0.0,
                "days_bucket": bucket_days(days),
                "image_count": len(embeddings)
            }

        prob = raw_prediction.get("probability", 0.0)
        public_prob = max(prob, self.MIN_PUBLIC_PROB)
        predicted_status = "Likely Found" if prob > 0.5 else "Unlikely Found"

        log_prediction(
            lost_pet_id=lost_pet_id,
            predicted_status=predicted_status,
            probability=prob,
            days_bucket=raw_prediction.get("days_bucket", bucket_days(days))
        )

        result = {
            "age": age,
            "days_missing": days,
            "barangay": barangay,
            "near_water": near_water_bool,
            "posted_on_fb": posted_on_fb_bool,
            "embeddings": embeddings,
            "similar_pets": similar_pets,
            "result_text": raw_prediction.get("result_text", "Unknown"),
            "prob": prob,
            "public_prob": public_prob,
            "days_bucket": raw_prediction.get("days_bucket", bucket_days(days)),
            "image_count": len(embeddings)
        }

        user_friendly = interpret_prediction(result, barangay=barangay)

        return {
            "result_text": f"{user_friendly['band']} ({user_friendly['probability']})",
            "reasons": user_friendly["reasons"],
            "actions": user_friendly["actions"],
            "num_images": len(embeddings),
            "similar_pets": similar_pets
        }