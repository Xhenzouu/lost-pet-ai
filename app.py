# app.py
import streamlit as st
from config import PAGE_TITLE, PAGE_ICON, LAYOUT
from model import load_model_artifacts, predict_reunion
from ui import render_form, show_results

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT
)

# -------------------------------
# Header
# -------------------------------
st.title("🐕🐈 Lost Pet Reunion Predictor for Pila, Laguna v4 🐇🐦🐢")
st.markdown("""
**Works for ANY pet: dogs, cats, rabbits, birds, hamsters, etc.!**  
Biggest factor: **Posting on Facebook = much higher chance!**  
Pila has ~57,776 people across 17 barangays — community power! 🐾
""")

# -------------------------------
# Load Model Artifacts
# -------------------------------
try:
    model, le_barangay = load_model_artifacts()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

# -------------------------------
# Render Form (UI)
# -------------------------------
defaults = {"age": 1.0, "days": 1, "barangay": "Pansol"}
submitted, pet_type, age, days, barangay, near_water, posted_on_fb = render_form(defaults=defaults)

# -------------------------------
# Handle Submission
# -------------------------------
if submitted:
    near_water_bool = 1 if near_water == "Yes" else 0
    posted_on_fb_bool = 1 if posted_on_fb == "Yes" else 0

    result_text, prob, days_bucket = predict_reunion(
        model, le_barangay, age, days, barangay, near_water_bool, posted_on_fb_bool
    )

    if "Error" in result_text:
        st.error(result_text)
    else:
        show_results(
            result_text=result_text,
            prob=prob,
            days_bucket=days_bucket,
            bucket_label_color_fn=lambda bucket: (
                {0: ("Very recent", "green"), 1: ("Recent", "yellow"),
                 2: ("Moderate", "orange"), 3: ("Long missing", "red")}
                .get(bucket, ("Unknown", "gray"))
            ),
            posted_on_fb=posted_on_fb
        )