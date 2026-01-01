# core/views/app_view.py
import streamlit as st
from core.ui import render_form, render_role_selection
from core.public_helpers import interpret_prediction
import cloudinary
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
            uploaded_file_urls = []

            # Upload files to Cloudinary
            if uploaded_files:
                for file in uploaded_files:
                    try:
                        file_bytes = file.getbuffer()
                        upload_result = cloudinary.uploader.upload(
                            io.BytesIO(file_bytes),
                            folder="pila_pets_ai",
                            resource_type="image"
                        )
                        uploaded_file_urls.append(upload_result["secure_url"])
                    except Exception as e:
                        st.error(f"❌ Failed to upload {file.name}: {e}")

            if uploaded_file_urls:
                st.markdown("**Uploaded Images Preview:**")
                for img_path in uploaded_file_urls:
                    st.image(img_path, width=200)

            # Handle submission
            result = self.controller.handle_submission(
                pet_type, age, days, barangay, near_water, posted_on_fb, uploaded_files
            )

            if "error" in result:
                st.error(result["error"])
                return

            st.markdown(f"### 🐾 Prediction: {result['result_text']}")
            st.markdown("**Reasons:**")
            for reason in result["reasons"]:
                st.write(f"• {reason}")
            st.markdown("**Recommended Actions:**")
            for action in result["actions"]:
                st.write(f"✅ {action}")