# core/controllers/dashboard_controller.py
from core.models.lost_pet_model import LostPetModel

class DashboardController:
    def __init__(self):
        self.model = LostPetModel()

    def get_filtered_submissions(self, pet_type, barangay, status, search):
        return self.model.get_submissions(pet_type, barangay, status, search)