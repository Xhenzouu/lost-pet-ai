# app.py
import streamlit as st

# -------------------------
# Page Config (must be first Streamlit call)
# -------------------------
st.set_page_config(
    page_title="🐕🐈 Lost Pet Reunion Predictor v6",
    page_icon="🐕🐈",
    layout="centered"
)

# -------------------------
# Load local .env if present
# -------------------------
import os
import traceback
import sqlalchemy
import cloudinary
from sqlalchemy import text

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    st.warning("⚠️ python-dotenv not installed, skipping local .env load.")

# -------------------------
# Config & core imports
# -------------------------
from core.config import PAGE_TITLE, PAGE_ICON, LAYOUT, ADMIN_PASSWORD, DB_URL, BARANGAYS
from core.controllers.app_controller import AppController
from core.views.app_view import AppView
from core.views.dashboard_view import DashboardView
from core.db.db import engine, SessionLocal
from core.models.lost_pet_model import (
    LostPetModel,
    compute_embedding_from_upload
)
from pathlib import Path

# -------------------------
# App Header
# -------------------------
st.title("🐕🐈 Lost Pet Reunion Predictor — Pila, Laguna v6 🐇🐦🐢")
st.markdown("""
**Works for ANY pet: dogs, cats, rabbits, birds, hamsters, etc.!**  
Biggest factor: **Posting on Facebook = much higher chance!**  
Pila has ~57,776 people across 17 barangays — community power! 🐾
""")

# -------------------------
# Startup Checks
# -------------------------
startup_errors = []

try:
    if not DB_URL or not engine:
        startup_errors.append("⚠️ Database not configured. DB_URL missing or engine not initialized.")
    else:
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
except Exception as e:
    startup_errors.append(f"⚠️ Database connection failed: {e}")

try:
    cfg = cloudinary.config()
    if not all([cfg.cloud_name, cfg.api_key, cfg.api_secret]):
        raise ValueError("Cloudinary config incomplete")
except Exception as e:
    startup_errors.append(f"⚠️ Cloudinary not configured properly: {e}")

def model_exists() -> bool:
    root = Path(__file__).resolve().parent / "pkl"
    return (root / "lost_pet_model_v5.pkl").exists() and (root / "le_barangay.pkl").exists()

if not model_exists():
    startup_errors.append(
        "⚠️ Model files missing in `/pkl`:\n- lost_pet_model_v5.pkl\n- le_barangay.pkl"
    )

if startup_errors:
    for err in startup_errors:
        st.error(err)
    st.stop()

# -------------------------
# Sidebar Role Selection
# -------------------------
role = st.sidebar.selectbox("Select Role", ["Guest", "Admin"])

# -------------------------
# Guest View with Tabs
# -------------------------
if role == "Guest":
    try:
        controller = AppController()

        tab_lost, tab_found = st.tabs(["🐕 Report Lost Pet", "🐾 Report Found Pet"])

        with tab_lost:
            view = AppView(controller)
            view.render()

        with tab_found:
            st.header("🐾 Report a Found Pet")
            st.markdown("""
            Help reunite a pet in Pila!  
            Upload clear photos (face or body preferred) of a pet you found.  
            We'll check against recent lost reports (only pets with photos shown).
            """)

            found_barangay = st.selectbox(
                "Barangay where the pet was found (optional)",
                [""] + BARANGAYS
            )

            found_photos = st.file_uploader(
                "Upload found pet photos (1–5)",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                key="found_uploader"
            )

            if st.button("Search for Matches", type="primary"):
                if not found_photos:
                    st.warning("Please upload at least one photo to search.")
                else:
                    with st.spinner("Processing photos and searching for matches..."):
                        embeddings = []
                        for photo in found_photos:
                            emb = compute_embedding_from_upload(photo)
                            if emb:
                                embeddings.append(emb)

                        if not embeddings:
                            st.error("Couldn't process any photos. Try clearer images or different angles.")
                        else:
                            query_emb = embeddings[0]
                            try:
                                LostPetModel._load_faiss_index()
                                scores, indices = LostPetModel.compute_similarity(query_emb, k=5)

                                if scores:
                                    st.success(f"Found {len(scores)} potential matches (only pets with photos)!")

                                    # Debug: show raw scores
                                    with st.expander("Debug: Raw Similarity Scores"):
                                        st.write([f"{s:.1%}" for s in scores])

                                    session = SessionLocal()
                                    try:
                                        shown_count = 0
                                        for i, (score, lost_id) in enumerate(zip(scores, indices), 1):
                                            if lost_id == -1:
                                                continue

                                            # INNER JOIN + ALL images for the matched pet
                                            query = text("""
                                                SELECT 
                                                    lp.pet_type, lp.age_years, lp.days_missing, lp.barangay,
                                                    pi.image_path
                                                FROM lost_pets lp
                                                INNER JOIN pet_images pi ON pi.lost_pet_id = lp.id
                                                WHERE lp.id = :lost_id
                                            """).bindparams(lost_id=lost_id)

                                            rows = session.execute(query).fetchall()

                                            if rows:
                                                # Basic info from first row
                                                pet_type = rows[0][0] or 'Unknown'
                                                age = rows[0][1] or 'Unknown'
                                                days_missing = rows[0][2]
                                                barangay = rows[0][3]

                                                # Show header with perfect match highlight
                                                if score >= 0.98:
                                                    st.success(f"**Perfect Match {i} ({score:.1%})** - This is likely the same pet!")
                                                elif score > 0.80:
                                                    st.markdown(f"**Strong Match {i} ({score:.1%})**")
                                                elif score > 0.70:
                                                    st.markdown(f"**Possible Match {i} ({score:.1%})**")
                                                else:
                                                    st.markdown(f"Match {i} ({score:.1%})")

                                                st.write(f"**Pet Type:** {pet_type}")
                                                st.write(f"**Age:** {age} years")
                                                st.write(f"**Missing for:** {days_missing} days")
                                                st.write(f"**Barangay:** {barangay}")

                                                # Show all photos for this matched lost pet
                                                st.markdown("**Similar Photos:**")
                                                if rows:
                                                    photo_cols = st.columns(min(4, len(rows)))
                                                    for j, row in enumerate(rows):
                                                        img_url = row[4]
                                                        if img_url:
                                                            photo_cols[j % 4].image(img_url, width=150)
                                                else:
                                                    st.write("No photos available (shouldn't happen)")

                                                st.markdown("---")
                                                shown_count += 1

                                        if shown_count == 0:
                                            st.info("No matches displayed (temporarily showing all for testing). Try a clearer photo!")

                                    finally:
                                        session.close()

                                else:
                                    st.info("No close matches found yet (only pets with photos are considered). Thank you for helping!")

                            except Exception as faiss_err:
                                st.error(f"Search failed: {str(faiss_err)}")
                                print(f"FAISS error: {faiss_err}")

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
        st.error("❌ ADMIN_PASSWORD not set in secrets or .env.")
    elif password_input == ADMIN_PASSWORD:
        st.success("✅ Admin access granted")
        st.info("⚠️ Dashboard shows a subset of training data. Use responsibly.")

        try:
            dashboard_view = DashboardView()
            dashboard_view.render(default_page_size=20)
        except Exception as e:
            st.error(f"❌ Failed to load dashboard: {type(e).__name__}: {e}")
            st.text(traceback.format_exc())
    elif password_input:
        st.error("❌ Incorrect password")
    else:
        st.info("Enter admin password to continue")