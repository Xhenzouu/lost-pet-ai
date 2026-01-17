# core/views/found_pet_view.py
import streamlit as st
from core.config import BARANGAYS
from PIL import Image
import io

class FoundPetView:
    def __init__(self, controller):
        self.controller = controller

    def render(self):
        st.header("🐾 Report a Found Pet")
        st.markdown("""
        Help reunite a pet in Pila!  
        Upload clear photos (face or body preferred) of a pet you found.  
        We'll check against recent lost reports.
        """)

        # Form
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
                    result = self.controller.handle_found_pet_submission(found_photos, found_barangay)

                    if "error" in result:
                        st.error(result["error"])
                    else:
                        self._display_results(result)

        # Preview uploaded photos
        if found_photos:
            st.markdown("**Uploaded Images Preview:**")
            cols = st.columns(min(3, len(found_photos)))
            for i, f in enumerate(found_photos):
                try:
                    f.seek(0)
                    img = Image.open(io.BytesIO(f.read()))
                    cols[i % 3].image(img, width=150, caption=f.name)
                except Exception:
                    cols[i % 3].warning(f"⚠️ Could not preview {f.name}")

    def _display_results(self, result):
        st.success(f"Checked against existing lost pets. Found {len(result['matches'])} potential matches.")

        if result["matches"]:
            for i, match in enumerate(result["matches"], 1):
                score = match["similarity"]
                lost_id = match["lost_pet_id"]
                pet_type = match["pet_type"]
                age = match["age"]
                days_missing = match["days_missing"]
                barangay = match["barangay"]
                image_paths = match["image_paths"]

                # Header
                if score > 0.75:
                    st.markdown(f"**Strong Match {i}:** {score:.1%} similarity → Lost Pet ID: {lost_id}")
                elif score > 0.60:
                    st.markdown(f"**Possible Match {i}:** {score:.1%} similarity → Lost Pet ID: {lost_id}")
                else:
                    st.markdown(f"Match {i}: Low similarity ({score:.1%}) → Lost Pet ID: {lost_id}")

                # Details
                st.write(f"**Pet Type:** {pet_type}")
                st.write(f"**Age:** {age} years")
                st.write(f"**Missing for:** {days_missing} days")
                st.write(f"**Barangay:** {barangay}")

                # Gallery of all photos for this match
                if image_paths:
                    st.markdown("**Similar Photos:**")
                    photo_cols = st.columns(min(4, len(image_paths)))
                    for j, url in enumerate(image_paths):
                        if url:
                            photo_cols[j % 4].image(url, width=150)
                else:
                    st.write("No photos available")

                st.markdown("---")

            st.info("If any look familiar, contact the barangay or us for next steps.")
        else:
            st.info("No close matches found yet. Thank you for helping a pet find home!")