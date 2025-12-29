# core/controllers/app_controller.py

from core.models.lost_pet_model import LostPetModel
from core.model import load_model_artifacts, predict_reunion
from core.db.db_utils import log_prediction
from core.views.dashboard_view import DashboardView
from core.public_helpers import interpret_prediction  # NEW

class AppController:
    def __init__(self):
        """
        Initialize controller:
        - Load trained ML model artifacts
        - Initialize admin dashboard view
        """
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
        uploaded_files
    ):
        """
        Handles form submission:
        1. Save lost pet record
        2. Save images + compute embeddings
        3. Run ML prediction
        4. Log prediction
        5. Return user-friendly v5 interpretation
        """

        # Convert Yes/No strings to numeric flags
        near_water_bool = 1 if near_water == "Yes" else 0
        posted_on_fb_bool = 1 if posted_on_fb == "Yes" else 0

        # -------------------------------
        # Save lost pet core data
        # -------------------------------
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

        # -------------------------------
        # Save images & compute embeddings
        # -------------------------------
        embeddings = []
        if uploaded_files:
            embeddings = LostPetModel.save_pet_images(
                lost_pet_id,
                uploaded_files
            )

        # -------------------------------
        # Predict reunion probability
        # -------------------------------
        raw_prediction = predict_reunion(
            model=self.model,
            le_barangay=self.le_barangay,
            age=age,
            days_missing=days,
            barangay=barangay,
            near_water=near_water_bool,
            posted_on_fb=posted_on_fb_bool,
            embeddings=embeddings
        )

        # -------------------------------
        # Log prediction result
        # -------------------------------
        log_prediction(
            lost_pet_id=lost_pet_id,
            result_label="Likely Found" if raw_prediction[1] > 0.5 else "Unlikely Found",
            probability=raw_prediction[1],
            days_bucket=raw_prediction[2]
        )

        # -------------------------------
        # Prepare raw result dict
        # -------------------------------
        result = {
            "age": age,
            "days_missing": days,
            "barangay": barangay,
            "near_water": near_water,
            "posted_on_fb": posted_on_fb,
            "embeddings": embeddings,
            "result_text": raw_prediction[0],
            "prob": raw_prediction[1],
            "days_bucket": raw_prediction[2]
        }

        # -------------------------------
        # Return v5 public-friendly interpretation
        # -------------------------------
        user_friendly = interpret_prediction(result, barangay=barangay)
        return {
            "result_text": f"{user_friendly['band']} ({user_friendly['probability']})",
            "reasons": user_friendly["reasons"],
            "actions": user_friendly["actions"],
            "num_images": len(embeddings)
        }