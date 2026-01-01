# core/views/app_view.py
import streamlit as st
from core.ui import render_form, render_role_selection
from core.public_helpers import interpret_prediction
from PIL import Image
import io

class AppView:
    def __init__(self, controller, admin_password="admin123"):
        self.controller = controller
        self.admin_password = admin_password

    def render(self):
        role, password_input = render_role_selection()

        if role == "Admin":
            if password_input == "":
                st.warning("Enter admin password and click 'Enter' to proceed.")
                return
            elif password_input != self.admin_password:
                st.error("❌ Incorrect admin password.")
                return
            else:
                st.success("✅ Admin access granted!")
                if hasattr(self.controller, "dashboard_view"):
                    self.controller.dashboard_view.render()
                return

        # Guest
        defaults = {"age": 1.0, "days": 1, "barangay": "Pansol"}
        submitted, pet_type, age, days, barangay, near_water, posted_on_fb, uploaded_files = render_form(defaults)

        if submitted:
            # Handle submission using controller
            result = self.controller.handle_submission(
                pet_type, age, days, barangay, near_water, posted_on_fb, uploaded_files
            )

            # Uploaded images preview
            if uploaded_files:
                st.markdown("**Uploaded Images Preview:**")
                for f in uploaded_files:
                    try:
                        f.seek(0)
                        img = Image.open(io.BytesIO(f.read()))
                        st.image(img, width=200)
                    except Exception:
                        st.warning(f"⚠️ Could not preview {f.name}")

            st.markdown(f"### 🐾 Prediction: {result['result_text']}")
            st.markdown("**Reasons:**")
            for reason in result["reasons"]:
                st.write(f"• {reason}")
            st.markdown("**Recommended Actions:**")
            for action in result["actions"]:
                st.write(f"✅ {action}")
            st.info(f"🔹 Number of embeddings used: {result['num_images']}")