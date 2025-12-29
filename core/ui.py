# core/ui.py
import streamlit as st
from typing import Optional, List, Tuple

BARANGAYS = [
    'Aplaya', 'Bagong Pook', 'Bukal', 'Bulilan Norte', 'Bulilan Sur',
    'Concepcion', 'Labuin', 'Linga', 'Masico', 'Mojon', 'Pansol',
    'Pinagbayanan', 'San Antonio', 'San Miguel', 'Santa Clara Norte',
    'Santa Clara Sur', 'Tubuan'
]

PET_TYPES = ["Dog", "Cat", "Rabbit", "Bird", "Hamster"]

# -------------------------------
# Guest Form
# -------------------------------
def render_form(defaults: Optional[dict] = None) -> Tuple[bool, str, float, int, str, str, str, List]:
    if defaults is None:
        defaults = {}
    with st.form("pet_form"):
        st.subheader("Enter your lost pet details 📝")
        pet_type = st.selectbox("Pet Type", options=PET_TYPES, index=PET_TYPES.index(defaults.get("pet_type", "Dog")))
        age = st.number_input("Age (years)", min_value=0.1, max_value=30.0, value=defaults.get("age", 2.0), step=0.5)
        days = st.number_input("Days missing", min_value=1, max_value=365, value=defaults.get("days", 3))
        default_barangay = defaults.get("barangay", "Pansol")
        barangay_index = BARANGAYS.index(default_barangay) if default_barangay in BARANGAYS else 0
        barangay = st.selectbox("Barangay", options=BARANGAYS, index=barangay_index)
        near_water = st.radio("Near Laguna de Bay or water area?", options=["Yes", "No"], index=0)
        posted_on_fb = st.radio("Already posted on Facebook or local groups?", options=["Yes", "No"], index=0)
        uploaded_files = st.file_uploader("Upload photos (optional)", type=["jpg","jpeg","png"], accept_multiple_files=True)
        submitted = st.form_submit_button("Predict Reunion Chance")
    return submitted, pet_type, age, days, barangay, near_water, posted_on_fb, uploaded_files

# -------------------------------
# Dashboard Search & Filters (Above Grid)
# -------------------------------
def render_search_filters(pet_types, barangays):
    cols = st.columns([2,2,2,1])
    with cols[0]:
        pet_type = st.selectbox("Pet Type", options=["All"] + pet_types)
    with cols[1]:
        barangay = st.selectbox("Barangay", options=["All"] + barangays)
    with cols[2]:
        status = st.selectbox("Prediction Status", options=["All", "Likely Found", "Unlikely Found", "Unknown"])
    with cols[3]:
        page_size = st.number_input("Page Size", min_value=5, max_value=100, value=20)
    search_text = st.text_input("Search by Name / Type / Barangay")
    return {"pet_type": pet_type, "barangay": barangay, "status": status, "search_text": search_text, "page_size": page_size}

# -------------------------------
# Show Results
# -------------------------------
def show_results(result_text, prob, days_bucket, bucket_label_color_fn, posted_on_fb):
    label, color = bucket_label_color_fn(days_bucket)
    st.subheader(f"📦 Days missing bucket: {days_bucket} — {label}")
    st.write(result_text)
    st.markdown("### Reunion Probability")
    st.progress(int(prob * 100))
    if prob > 0.5:
        st.balloons()
        st.success("🎉 Good chance of reunion!")
        if posted_on_fb == "Yes":
            st.info("👏 Salamat sa pag-post sa FB — malaking tulong 'yan!'")
        st.info("💡 Next: Maglagay ng flyers sa plaza, magtanong sa kapitbahay, hanapin sa nearby barangays.")
    else:
        if posted_on_fb == "No":
            st.warning("⚠️ POST ON FACEBOOK AGAD — malaking difference!")
        st.info("💡 Huwag mawalan ng pag-asa! Keep sharing daily in groups.")
    st.markdown("### Recommended groups: Pila Laguna Residents & Missing Pets Philippines 🐾")
    with st.expander("💡 Tips & Advice"):
        st.write("""
        - Post daily updates and photos in local Facebook groups.
        - Make and distribute flyers in nearby barangays.
        - Check with neighbors and barangay officials.
        - Visit local markets, parks, and areas near water bodies.
        - Stay calm and persistent — many pets are found days later.
        """)
    st.caption("Salamat po sa paggamit! Always post lost pets online — it really works in Pila! 🐾")

# -------------------------------
# Role Selection UI (Guest default, Admin button)
# -------------------------------
def render_role_selection() -> Tuple[str, str]:
    st.sidebar.header("Access Options")
    role = "Guest"  # default
    password_input = ""
    submitted = False

    # Button to switch to Admin
    admin_mode = st.sidebar.checkbox("Login as Admin")
    if admin_mode:
        role = "Admin"
        password_input = st.sidebar.text_input("Enter admin password", type="password")
        submitted = st.sidebar.button("Enter")  # explicit submit

        if not submitted:
            password_input = ""  # ignore password until Enter clicked

    return role, password_input