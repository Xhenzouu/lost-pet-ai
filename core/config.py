import os
import cloudinary
from dotenv import load_dotenv

load_dotenv()

PAGE_TITLE = "Lost Pet Reunion Predictor v5"
PAGE_ICON = "🐕🐈"
LAYOUT = "centered"

if os.getenv("STREAMLIT_ENV") == "production":
    import streamlit as st
    try:
        ADMIN_PASSWORD = st.secrets["auth"]["ADMIN_PASSWORD"]
    except Exception:
        ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "no_access_can_do")
else:
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "no_access_can_do")

DB_ENV = os.getenv("DB_ENV", "local").lower()
if DB_ENV == "prod":
    try:
        import streamlit as st
        DB_URL = st.secrets["postgres"]["DB_URL"]
    except Exception:
        DB_URL = os.getenv("DB_URL_PROD")
else:
    DB_URL = os.getenv("DB_URL_LOCAL")

if os.getenv("STREAMLIT_ENV") == "production":
    import streamlit as st
    try:
        cloud_name = st.secrets["cloudinary"]["CLOUDINARY_CLOUD_NAME"]
        api_key = st.secrets["cloudinary"]["CLOUDINARY_API_KEY"]
        api_secret = st.secrets["cloudinary"]["CLOUDINARY_API_SECRET"]
    except Exception:
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")
else:
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret
)

BARANGAYS = [
    "Aplaya", "Bagong Pook", "Bukal", "Bulilan Norte", "Bulilan Sur",
    "Concepcion", "Labuin", "Linga", "Masico", "Mojon", "Pansol",
    "Pinagbayanan", "San Antonio", "San Miguel",
    "Santa Clara Norte", "Santa Clara Sur", "Tubuan"
]

PET_TYPES = {
    "Dog": "🐕",
    "Cat": "🐈",
    "Rabbit": "🐇",
    "Bird": "🐦",
    "Turtle": "🐢",
    "Hamster": "🐹",
    "Other": "🐾",
}

BUCKET_COLORS = {
    0: ("Very recent", "#a8e6cf"),
    1: ("Recent", "#ffd3b6"),
    2: ("Moderate", "#ffaaa5"),
    3: ("Long missing", "#ff8b94"),
}

DEFAULT_AGE = 0.0
DEFAULT_DAYS = 1
DEFAULT_BRG = "Pansol"
DEFAULT_NEAR_WATER = "No"
DEFAULT_POSTED_ON_FB = "No"