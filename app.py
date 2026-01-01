# app.py
import streamlit as st
from pathlib import Path
from core.config import PAGE_TITLE, PAGE_ICON, LAYOUT, ADMIN_PASSWORD
from core.controllers.app_controller import AppController
from core.views.app_view import AppView
from core.views.dashboard_view import DashboardView
import traceback
import cloudinary  # production requires Cloudinary

# -------------------------
# Page Config
# -------------------------
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)

# Header
st.title("🐕🐈 Lost Pet Reunion Predictor — Pila, Laguna v5 🐇🐦🐢")
st.markdown("""
**Works for ANY pet: dogs, cats, rabbits, birds, hamsters, etc.!**  
Biggest factor: **Posting on Facebook = much higher chance!**  
Pila has ~57,776 people across 17 barangays — community power! 🐾
""")

# Sidebar Role Selection
role = st.sidebar.selectbox("Select Role", ["Guest", "Admin"])

# -------------------------
# Check Model Files
# -------------------------
def model_exists() -> bool:
    root = Path(__file__).resolve().parent
    pkl = root / "pkl"
    return (pkl / "lost_pet_model_v5.pkl").exists() and (pkl / "le_barangay.pkl").exists()

# -------------------------
# Guest View
# -------------------------
if role == "Guest":
    if not model_exists():
        st.warning(
            "⚠️ Model files not found.\n\n"
            "Required files in `/pkl`:\n"
            "- lost_pet_model_v5.pkl\n"
            "- le_barangay.pkl"
        )
    else:
        try:
            controller = AppController()
            view = AppView(controller)
            view.render()
        except Exception as e:
            st.error(f"❌ Failed to load Guest view: {type(e).__name__}: {e}")
            st.text(traceback.format_exc())

# -------------------------
# Admin View
# -------------------------
else:
    st.sidebar.markdown("### 🔐 Admin Login")
    password_input = st.sidebar.text_input("Enter admin password", type="password")

    if not ADMIN_PASSWORD:
        st.error("❌ ADMIN_PASSWORD not set in .env.")
    elif password_input == ADMIN_PASSWORD:
        st.success("✅ Admin access granted")
        st.info("⚠️ Dashboard shows a subset of training data. Use responsibly.")

        if model_exists():
            try:
                dashboard_view = DashboardView()
                dashboard_view.render(default_page_size=20)
            except Exception as e:
                st.error(f"❌ Failed to load dashboard: {type(e).__name__}: {e}")
                st.text(traceback.format_exc())
        else:
            st.warning("⚠️ Model files missing. Dashboard may be incomplete.")
    elif password_input:
        st.error("❌ Incorrect password")
    else:
        st.info("Enter admin password to continue")