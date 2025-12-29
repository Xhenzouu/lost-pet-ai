# core/views/dashboard_view.py
import streamlit as st
from pathlib import Path
from core.controllers.dashboard_controller import DashboardController
from core.db.db import SessionLocal
from core.ui import render_search_filters  # Use base UI
from sqlalchemy import text
from PIL import Image

BARANGAYS = [
    'Aplaya', 'Bagong Pook', 'Bukal', 'Bulilan Norte', 'Bulilan Sur',
    'Concepcion', 'Labuin', 'Linga', 'Masico', 'Mojon', 'Pansol',
    'Pinagbayanan', 'San Antonio', 'San Miguel', 'Santa Clara Norte',
    'Santa Clara Sur', 'Tubuan'
]
PET_TYPES = ["Dog", "Cat", "Rabbit", "Bird", "Hamster"]

class DashboardView:
    def __init__(self):
        self.controller = DashboardController()

    def render(self, default_page_size=20):
        st.title("📊 Lost Pet Admin Dashboard — Pila, Laguna")

        # ---------------------------
        # Search & Filters (Above Grid)
        # ---------------------------
        filters = render_search_filters(PET_TYPES, BARANGAYS)
        pet_type_filter = filters["pet_type"]
        barangay_filter = filters["barangay"]
        status_filter = filters["status"]
        search_text = filters["search_text"]
        page_size_input = filters["page_size"]

        # Initialize pagination state
        if "page_number" not in st.session_state:
            st.session_state.page_number = 1

        prev_page, next_page = st.columns([1, 1])
        with prev_page:
            if st.button("⬅️ Previous"):
                if st.session_state.page_number > 1:
                    st.session_state.page_number -= 1
        with next_page:
            if st.button("➡️ Next"):
                st.session_state.page_number += 1

        # ---------------------------
        # Load Filtered Data
        # ---------------------------
        submissions = self.controller.get_filtered_submissions(
            pet_type_filter, barangay_filter, status_filter, search_text
        )

        total_submissions = len(submissions)
        total_pages = max(1, (total_submissions + page_size_input - 1) // page_size_input)
        st.session_state.page_number = min(st.session_state.page_number, total_pages)

        start_idx = (st.session_state.page_number - 1) * page_size_input
        end_idx = start_idx + page_size_input
        current_submissions = submissions[start_idx:end_idx]

        st.markdown(f"### Total Submissions: {total_submissions} — Page {st.session_state.page_number} of {total_pages}")
        st.markdown("---")

        # ---------------------------
        # Display Submissions in Cards (3 per row)
        # ---------------------------
        cols_per_row = 3
        for idx, row in enumerate(current_submissions):
            col_idx = idx % cols_per_row
            if col_idx == 0:
                cols = st.columns(cols_per_row)
            with cols[col_idx]:
                self.render_pet_card(row)
                st.divider()

    # ---------------------------
    # Render single pet card
    # ---------------------------
    def render_pet_card(self, row):
        pet_name = row.pet_name or "Unknown"
        pet_type = row.pet_type or "Unknown"
        age = getattr(row, "age_years", 0)
        days_missing = getattr(row, "days_missing", 0)
        barangay = row.barangay or "Unknown"
        near_water = "Yes" if row.near_water else "No"
        posted_on_fb = "Yes" if row.posted_on_fb else "No"
        found_at = row.found_at.strftime("%Y-%m-%d") if getattr(row, "found_at", None) else "Not Found Yet"
        predicted_status = row.predicted_status or "Unknown"
        probability = row.probability * 100 if getattr(row, "probability", None) else 0
        days_bucket = row.days_missing_bucket if getattr(row, "days_missing_bucket", None) is not None else "Unknown"

        st.markdown(f"### 🐾 {pet_name}")
        st.markdown(f"**Type:** {pet_type}")
        st.markdown(f"**Age:** {age:.2f} | **Days Missing:** {days_missing}")
        st.markdown(f"**Barangay:** {barangay}")
        st.markdown(f"**Near Water:** {near_water} | **Posted on FB:** {posted_on_fb}")
        st.markdown(f"**Prediction:** {predicted_status} ({probability:.1f}%) — Bucket: {days_bucket}")
        st.markdown(f"**Found At:** {found_at}")

        self.render_pet_images(row.id)

    # ---------------------------
    # Load & Render Images
    # ---------------------------
    def render_pet_images(self, lost_pet_id):
        session = SessionLocal()
        try:
            images = session.execute(
                text("SELECT image_path FROM pet_images WHERE lost_pet_id = :id"),
                {"id": lost_pet_id}
            ).fetchall()
            if images:
                cols_imgs = st.columns(len(images))
                for col_img, img_row in zip(cols_imgs, images):
                    img_path = Path(img_row.image_path)
                    if img_path.exists():
                        img = Image.open(img_path)
                        col_img.image(img, use_column_width=True)
        finally:
            session.close()