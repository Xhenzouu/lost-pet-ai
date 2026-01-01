# core/public_helpers.py

from typing import Dict, Any

# ------------------------------------------
# Public Helper: interpret probability
# ------------------------------------------
def interpret_probability(prob: float) -> str:
    """
    Convert raw probability into a human-friendly band.
    """
    if prob is None:
        return "Unknown"

    if prob < 0.3:
        return "Low chance"
    elif prob < 0.65:
        return "Moderate chance"
    else:
        return "High chance"


# ------------------------------------------
# Public Helper: generate reason explanations
# ------------------------------------------
def generate_reasons(input_data: Dict[str, Any]) -> list:
    """
    Provide plain-language reasons why the probability is high/low.
    Expects keys: days_bucket, posted_on_fb, near_water
    """
    reasons = []

    days_bucket = input_data.get("days_bucket")
    posted_on_fb = input_data.get("posted_on_fb")
    near_water = input_data.get("near_water")

    # Days missing
    if days_bucket is not None:
        if days_bucket == 0:
            reasons.append("Your pet was lost very recently.")
        elif days_bucket == 1:
            reasons.append("Your pet has been missing for a few days.")
        elif days_bucket == 2:
            reasons.append("Your pet has been missing for over a week.")
        else:
            reasons.append("Your pet has been missing for a long time.")

    # Facebook post
    if posted_on_fb == 1:
        reasons.append("The pet has been posted on Facebook groups.")
    else:
        reasons.append("The pet has not been posted on Facebook yet.")

    # Near water
    if near_water == 1:
        reasons.append("The pet may be near water, which can affect recovery.")

    return reasons


# ------------------------------------------
# Public Helper: action recommendations
# ------------------------------------------
def generate_actions(input_data: Dict[str, Any], barangay: str) -> list:
    """
    Return actionable steps in plain language.
    """
    actions = []

    posted_on_fb = input_data.get("posted_on_fb")
    image_count = input_data.get("image_count", 0)

    # Facebook posting
    if posted_on_fb != 1:
        actions.append("Post your pet in Pila Lost & Found Pets Facebook groups today.")

    # Barangay-specific
    if barangay:
        actions.append(f"Visit your Barangay Hall ({barangay}) to report the lost pet.")

    # Images
    if image_count == 0:
        actions.append("Add clear photos of your pet for better recognition.")
    else:
        actions.append("Ensure the photos of your pet are clear and recent.")

    # Safety disclaimer
    actions.append("Remember: These are recommendations and do not guarantee reunion.")

    return actions


# ------------------------------------------
# Public Helper: full interpretation
# ------------------------------------------
def interpret_prediction(prediction: Dict[str, Any], barangay: str) -> Dict[str, Any]:
    """
    Takes the raw prediction dict from core.model.predict_reunion()
    and returns a user-friendly dictionary suitable for Streamlit display.
    Probability is returned as a float, not a string.
    """
    probability = prediction.get("probability") or 0.0  # fallback to 0.0
    days_bucket = prediction.get("days_bucket")
    posted_on_fb = prediction.get("posted_on_fb")
    near_water = prediction.get("near_water")
    image_count = prediction.get("image_count", 0)

    input_data = {
        "days_bucket": days_bucket,
        "posted_on_fb": posted_on_fb,
        "near_water": near_water,
        "image_count": image_count
    }

    return {
        "band": interpret_probability(probability),
        "probability": probability,  # <-- return as float
        "reasons": generate_reasons(input_data),
        "actions": generate_actions(input_data, barangay)
    }