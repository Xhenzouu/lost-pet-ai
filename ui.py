# ui.py
import streamlit as st

# -------------------------------
# Constants
# -------------------------------
BARANGAYS = [
    'Aplaya', 'Bagong Pook', 'Bukal', 'Bulilan Norte', 'Bulilan Sur',
    'Concepcion', 'Labuin', 'Linga', 'Masico', 'Mojon', 'Pansol',
    'Pinagbayanan', 'San Antonio', 'San Miguel', 'Santa Clara Norte',
    'Santa Clara Sur', 'Tubuan'
]

PET_TYPES = ["Dog", "Cat", "Rabbit", "Bird", "Hamster"]

# -------------------------------
# Render Form
# -------------------------------
def render_form(defaults=None):
    if defaults is None:
        defaults = {}

    with st.form("pet_form"):
        st.subheader("Enter your lost pet details 📝")

        pet_type = st.selectbox(
            "Pet Type",
            options=PET_TYPES,
            index=0
        )

        age = st.number_input(
            "Age (years)",
            min_value=0.1,
            max_value=30.0,
            value=defaults.get("age", 2.0),
            step=0.5
        )

        days = st.number_input(
            "Days missing",
            min_value=1,
            max_value=365,
            value=defaults.get("days", 3)
        )

        barangay = st.selectbox(
            "Barangay",
            options=BARANGAYS,
            index=BARANGAYS.index(defaults.get("barangay","Pansol")) if defaults.get("barangay") else BARANGAYS.index("Pansol")
        )

        near_water = st.radio(
            "Near Laguna de Bay or water area?",
            options=["Yes", "No"],
            index=0
        )

        posted_on_fb = st.radio(
            "Already posted on Facebook or local groups?",
            options=["Yes", "No"],
            index=0
        )

        submitted = st.form_submit_button("Predict Reunion Chance")

    return submitted, pet_type, age, days, barangay, near_water, posted_on_fb


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

    # Collapsible Tips & Advice
    with st.expander("💡 Tips & Advice"):
        st.write("""
        - Post daily updates and photos in local Facebook groups.
        - Make and distribute flyers in nearby barangays.
        - Check with neighbors and barangay officials.
        - Visit local markets, parks, and areas near water bodies.
        - Stay calm and persistent — many pets are found days later.
        """)

    st.caption("Salamat po sa paggamit! Always post lost pets online — it really works in Pila! 🐾")