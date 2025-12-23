# config.py

# Page and app settings
PAGE_TITLE = "Lost Pet Reunion Predictor v4"
PAGE_ICON = "🐕🐈"
LAYOUT = "centered"

# Barangays in Pila, Laguna
BARANGAYS = [
    'Aplaya', 'Bagong Pook', 'Bukal', 'Bulilan Norte', 'Bulilan Sur',
    'Concepcion', 'Labuin', 'Linga', 'Masico', 'Mojon', 'Pansol',
    'Pinagbayanan', 'San Antonio', 'San Miguel', 'Santa Clara Norte',
    'Santa Clara Sur', 'Tubuan'
]

# Pet types with icons
PET_TYPES = {
    "Dog": "🐕",
    "Cat": "🐈",
    "Rabbit": "🐇",
    "Bird": "🐦",
    "Turtle": "🐢",
    "Hamster": "🐹",
    "Other": "🐾"
}

# Bucket colors for days_missing_bucket
BUCKET_COLORS = {
    0: ("Very recent", "#a8e6cf"),
    1: ("Recent", "#ffd3b6"),
    2: ("Moderate", "#ffaaa5"),
    3: ("Long missing", "#ff8b94")
}

# Default form values
DEFAULT_AGE = 0.0
DEFAULT_DAYS = 1
DEFAULT_BRG = 'Pansol'
DEFAULT_NEAR_WATER = "No"
DEFAULT_POSTED_ON_FB = "No"