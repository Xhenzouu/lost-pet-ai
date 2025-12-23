import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent

# App title
st.title("🐕🐈 Lost Pet Reunion Predictor for Pila, Laguna v4 🐇🐦🐢")

st.markdown("""
**Works for ANY pet: dogs, cats, rabbits, birds, hamsters, etc.!**  
Biggest factor: **Posting on Facebook = much higher chance!**  
Pila has ~57,776 people across 17 barangays — community power! 🐾
""")

# Load model
try:
    model = joblib.load(BASE_DIR / "lost_pet_model.pkl")
    le_barangay = joblib.load(BASE_DIR / "le_barangay.pkl")
except:
    st.error("Model files not found. Make sure 'lost_pet_model.pkl' and 'le_barangay.pkl' are in the same folder.")
    st.stop()

# Barangays
barangays = [
    'Aplaya', 'Bagong Pook', 'Bukal', 'Bulilan Norte', 'Bulilan Sur',
    'Concepcion', 'Labuin', 'Linga', 'Masico', 'Mojon', 'Pansol',
    'Pinagbayanan', 'San Antonio', 'San Miguel', 'Santa Clara Norte',
    'Santa Clara Sur', 'Tubuan'
]

# Features list
features = [
    "age_years",
    "days_missing",
    "days_missing_bucket",  # NEW v4 feature
    "near_water",
    "posted_on_fb",
    "barangay_encoded"
]

# Bucket function
def bucket_days(days):
    if days <= 3:
        return 0
    elif days <= 7:
        return 1
    elif days <= 14:
        return 2
    else:
        return 3

# Prediction function
def predict_reunion(age, days_missing, barangay_input, near_water, posted_on_fb):
    # Barangay encoding
    matches = [b for b in barangays if barangay_input.strip().lower() in b.lower()]
    if not matches:
        return "Error: Barangay not found. Please select from the list."
    barangay = matches[0]
    barangay_encoded = le_barangay.transform([barangay])[0]

    # Compute bucket
    days_bucket = bucket_days(days_missing)

    # Build input
    input_df = pd.DataFrame([[age, days_missing, days_bucket, near_water, posted_on_fb, barangay_encoded]],
                            columns=features)
    
    prob = model.predict_proba(input_df)[0][1]
    status = "Likely Found" if prob > 0.5 else "Unlikely Found"
    return f"Probability of being found: {prob:.1%} → {status}", prob

# Form
with st.form("pet_form"):
    st.subheader("Enter details of your lost pet")
    
    age = st.number_input("Age in years (e.g., 2 or 1.5)", min_value=0.1, max_value=30.0, value=2.0, step=0.5)
    days = st.number_input("Days missing", min_value=1, max_value=365, value=3)
    barangay = st.selectbox("Barangay", options=barangays, index=barangays.index('Pansol') if 'Pansol' in barangays else 0)
    near_water = st.radio("Near Laguna de Bay or water area?", options=["Yes", "No"], index=0)
    posted_on_fb = st.radio("Already posted on Facebook or local groups?", options=["Yes", "No"], index=0)
    
    submitted = st.form_submit_button("Predict Reunion Chance")

if submitted:
    near_water_bool = 1 if near_water == "Yes" else 0
    posted_on_fb_bool = 1 if posted_on_fb == "Yes" else 0
    
    result, prob = predict_reunion(age, days, barangay, near_water_bool, posted_on_fb_bool)
    
    if "Error" in result:
        st.error(result)
    else:
        st.success(result)
        if prob > 0.5:
            st.balloons()
            st.markdown("### 🎉 Good chance of reunion!")
            if posted_on_fb == "Yes":
                st.info("👏 Salamat sa pag-post sa FB — malaking tulong 'yan!'")
            st.info("💡 Next: Maglagay ng flyers sa plaza, magtanong sa kapitbahay, hanapin sa nearby barangays.")
        else:
            if posted_on_fb == "No":
                st.warning("⚠️ POST ON FACEBOOK AGAD — malaki ang magiging difference!")
            st.info("💡 Huwag mawalan ng pag-asa! Keep sharing daily sa groups.")
        
        st.markdown("### Recommended groups: Pila Laguna Residents & Missing Pets Philippines 🐾")

st.caption("Salamat po sa paggamit! Always post lost pets online — it really works in Pila! 🐾")