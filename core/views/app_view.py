# core/views/app_view.py
import streamlit as st
from core.ui import render_form, render_role_selection
from core.public_helpers import interpret_prediction  # NEW

class AppView:
    def __init__(self, controller, admin_password="admin123"):
        """
        controller: instance of your main app controller
        admin_password: default admin password (can be overridden)
        """
        self.controller = controller
        self.admin_password = admin_password

    def render(self):
        # -----------------------------
        # Role Selection
        # -----------------------------
        role, password_input = render_role_selection()

        if role == "Admin":
            if password_input == "":
                st.warning("Enter admin password and click 'Enter' to proceed.")
                return
            elif password_input != self.admin_password:
                st.error("❌ Incorrect admin password.")
                return
            else:
                # Password correct: show admin dashboard
                st.success("✅ Admin access granted!")
                if hasattr(self.controller, "dashboard_view"):
                    self.controller.dashboard_view.render()
                else:
                    st.info("Admin dashboard not initialized.")
                return  # stop here for Admin

        # -----------------------------
        # Guest view (default)
        # -----------------------------
        defaults = {"age": 1.0, "days": 1, "barangay": "Pansol"}
        submitted, pet_type, age, days, barangay, near_water, posted_on_fb, uploaded_files = render_form(defaults)

        if submitted:
            result = self.controller.handle_submission(
                pet_type, age, days, barangay, near_water, posted_on_fb, uploaded_files
            )

            if "error" in result:
                st.error(result["error"])
                return

            # -----------------------------
            # Interpret result for v5 (public)
            # -----------------------------
            user_friendly = interpret_prediction(result, barangay=barangay)

            # -----------------------------
            # Display summary
            # -----------------------------
            st.markdown(f"### 🐾 Prediction: {user_friendly['band']} ({user_friendly['probability']})")

            # -----------------------------
            # Display reasons
            # -----------------------------
            st.markdown("**Reasons:**")
            for reason in user_friendly["reasons"]:
                st.write(f"• {reason}")

            # -----------------------------
            # Display recommended actions
            # -----------------------------
            st.markdown("**Recommended Actions:**")
            for action in user_friendly["actions"]:
                st.write(f"✅ {action}")