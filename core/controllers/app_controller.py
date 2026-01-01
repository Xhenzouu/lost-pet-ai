# core/controllers/app_controller.py

from core.models.lost_pet_model import LostPetModel
from core.model import load_model_artifacts, predict_reunion
from core.db.db_utils import log_prediction
from core.views.dashboard_view import DashboardView
from core.public_helpers import interpret_prediction

class AppController:
    def __init__(self):
        self.model, self.le_barangay = load_model_artifacts()
        self.dashboard_view = DashboardView()

    def handle_submission(
        self,
        pet_type,
        age,
        days,
        barangay,
        near_water,
        posted_on_fb,
        uploaded_files_or_urls
    ):
        near_water_bool = True if near_water == "Yes" else False
        posted_on_fb_bool = True if posted_on_fb == "Yes" else False

        # Save lost pet
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

        # Save images & compute embeddings
        embeddings = LostPetModel.save_pet_images(lost_pet_id, uploaded_files_or_urls)

        # Predict reunion
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

        predicted_status = "Likely Found" if raw_prediction["probability"] > 0.5 else "Unlikely Found"

        # Log prediction
        log_prediction(
            lost_pet_id=lost_pet_id,
            predicted_status=predicted_status,
            probability=raw_prediction["probability"],
            days_bucket=raw_prediction["days_bucket"]
        )

        result = {
            "age": age,
            "days_missing": days,
            "barangay": barangay,
            "near_water": near_water,
            "posted_on_fb": posted_on_fb,
            "embeddings": embeddings,
            "result_text": raw_prediction["result_text"],
            "prob": raw_prediction["probability"],
            "days_bucket": raw_prediction["days_bucket"]
        }

        user_friendly = interpret_prediction(result, barangay=barangay)
        return {
            "result_text": f"{user_friendly['band']} ({user_friendly['probability']})",
            "reasons": user_friendly["reasons"],
            "actions": user_friendly["actions"],
            "num_images": len(embeddings)
        }