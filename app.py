# app.py
import streamlit as st
from core.controllers.app_controller import AppController
from core.views.app_view import AppView
from core.views.dashboard_view import DashboardView
from core.config import PAGE_TITLE, PAGE_ICON, LAYOUT
from pathlib import Path

# Pillow and numpy safe imports
from PIL import Image
import numpy as np

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)

# -------------------------------
# Header
# -------------------------------
st.title("🐕🐈 Lost Pet Reunion Predictor — Pila, Laguna v5 🐇🐦🐢")
st.markdown("""
**Works for ANY pet: dogs, cats, rabbits, birds, hamsters, etc.!**  
Biggest factor: **Posting on Facebook = much higher chance!**  
Pila has ~57,776 people across 17 barangays — community power! 🐾
""")

# -------------------------------
# Role Selection
# -------------------------------
role = st.sidebar.selectbox("Select Role", options=["Guest", "Admin"])

# -------------------------------
# Function to check if model exists
# -------------------------------
def model_exists():
    project_root = Path(__file__).resolve().parent
    pkl_dir = project_root / "pkl"                  
    model_file = pkl_dir / "lost_pet_model_v5.pkl"
    le_file = pkl_dir / "le_barangay.pkl"
    return model_file.exists() and le_file.exists()

# -------------------------------
# Guest View
# -------------------------------
if role == "Guest":
    if model_exists():
        try:
            controller = AppController()
            view = AppView(controller)
            view.render()
        except Exception as e:
            st.error(f"⚠️ Failed to load the model: {e}")
    else:
        st.warning(
            "⚠️ Model files not found. Please ensure the 'pkl' folder contains:\n"
            "- lost_pet_model_v5.pkl\n- le_barangay.pkl\n\n"
            "Guest functionality is unavailable until the model is present."
        )

# -------------------------------
# Admin View
# -------------------------------
elif role == "Admin":
    st.sidebar.markdown("### Admin Login")
    password_input = st.sidebar.text_input("Enter admin password", type="password")
    ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD")

    if password_input == ADMIN_PASSWORD:
        st.success("✅ Password correct — Access granted")
        st.info(
            "⚠️ Disclaimer: The data displayed in this dashboard is only a portion of the "
            "training dataset for the AI model. Use responsibly!"
        )

        if model_exists():
            try:
                dashboard_view = DashboardView()
                dashboard_view.render(default_page_size=20)
            except Exception as e:
                st.error(f"⚠️ Failed to load the dashboard: {e}")
        else:
            st.warning(
                "⚠️ Model files not found. Admin dashboard may not display correctly. "
                "Ensure the 'pkl' folder contains the model and encoder files."
            )

    elif password_input:
        st.error("❌ Incorrect password")
    else:
        st.info("Enter admin password to access dashboard")