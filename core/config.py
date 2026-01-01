# core/config.py

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PAGE_TITLE = "Lost Pet Reunion Predictor v5"
PAGE_ICON = "🐕🐈"
LAYOUT = "centered"

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

DB_URL = os.getenv("DB_URL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")