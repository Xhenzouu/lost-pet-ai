from typing import Dict, Any

def interpret_probability(prob: float) -> str:
    if prob is None:
        return "Unknown"
    if prob < 0.3:
        return "Low chance"
    elif prob < 0.65:
        return "Moderate chance"
    else:
        return "High chance"

def generate_reasons(input_data: Dict[str, Any]) -> list:
    reasons = []
    days_bucket = input_data.get("days_bucket")
    posted_on_fb = int(input_data.get("posted_on_fb", 0))
    near_water = int(input_data.get("near_water", 0))

    if days_bucket is not None:
        if days_bucket == 0:
            reasons.append("Your pet was lost very recently.")
        elif days_bucket == 1:
            reasons.append("Your pet has been missing for a few days.")
        elif days_bucket == 2:
            reasons.append("Your pet has been missing for over a week.")
        else:
            reasons.append("Your pet has been missing for a long time.")

    reasons.append(
        "The pet has been posted on Facebook groups."
        if posted_on_fb == 1 else
        "The pet has not been posted on Facebook yet."
    )

    if near_water == 1:
        reasons.append("The pet may be near water, which can affect recovery.")

    return reasons

def generate_actions(input_data: Dict[str, Any], barangay: str) -> list:
    actions = []
    posted_on_fb = int(input_data.get("posted_on_fb", 0))
    image_count = input_data.get("image_count", 0)

    if posted_on_fb != 1:
        actions.append("Post your pet in Pila Lost & Found Pets Facebook groups today.")
    if barangay:
        actions.append(f"Visit your Barangay Hall ({barangay}) to report the lost pet.")
    if image_count == 0:
        actions.append("Add clear photos of your pet for better recognition.")
    elif image_count > 0:
        actions.append("Ensure the photos of your pet are clear and recent.")

    actions.append("Remember: These are recommendations and do not guarantee reunion.")
    return actions

def interpret_prediction(prediction: Dict[str, Any], barangay: str) -> Dict[str, Any]:
    probability = prediction.get("public_prob", prediction.get("probability", 0.0))
    probability = max(0.0, min(probability, 1.0))

    input_data = {
        "days_bucket": prediction.get("days_bucket"),
        "posted_on_fb": prediction.get("posted_on_fb"),
        "near_water": prediction.get("near_water"),
        "image_count": prediction.get("image_count", 0)
    }

    probability_str = f"{probability*100:.1f}%"

    return {
        "band": interpret_probability(probability),
        "probability": probability_str,
        "reasons": generate_reasons(input_data),
        "actions": generate_actions(input_data, barangay)
    }