import pandas as pd
import joblib

# Load dataset for display
print("Loading Pila lost pets dataset...\n")
df = pd.read_csv('lost_pets_pila_dataset.csv')

print("Dataset loaded! First 10 rows:")
print(df.head(10))
print("\nFound distribution:")
print(df['found'].value_counts(normalize=True))

# Load pre-trained model and barangay encoder (no pet encoder anymore)
print("\nLoading pre-trained model (works for ANY pet)...")
model = joblib.load('lost_pet_model.pkl')
le_barangay = joblib.load('le_barangay.pkl')

# Complete 17 barangays of Pila, Laguna (2025)
barangays = [
    'Aplaya', 'Bagong Pook', 'Bukal', 'Bulilan Norte', 'Bulilan Sur',
    'Concepcion', 'Labuin', 'Linga', 'Masico', 'Mojon', 'Pansol',
    'Pinagbayanan', 'San Antonio', 'San Miguel', 'Santa Clara Norte',
    'Santa Clara Sur', 'Tubuan'
]

# Features — no pet_type!
features = ['age_years', 'days_missing', 'near_water', 'posted_on_fb', 'barangay_encoded']

print("Model ready for predictions!\n")

# Prediction function — no pet input needed
def predict_reunion(age_years, days_missing, barangay_input, near_water, posted_on_fb):
    # Flexible barangay matching
    barangay_lower = barangay_input.strip().lower()
    matches = [b for b in barangays if barangay_lower in b.lower()]
    if not matches:
        return "Error: Barangay not found. Try: Pansol, Aplaya, Bukal, Labuin, Santa Clara, etc."
    barangay = matches[0]

    barangay_encoded = le_barangay.transform([barangay])[0]

    # Predict
    input_df = pd.DataFrame([[age_years, days_missing, near_water, posted_on_fb, barangay_encoded]],
                            columns=features)
    
    prob = model.predict_proba(input_df)[0][1]
    status = "Likely Found" if prob > 0.5 else "Unlikely Found"
    return f"Probability of being found: {prob:.1%} → {status}"

# Header — now truly for any pet
print("="*85)
print("     LOST ANY PET REUNION PREDICTOR FOR PILA, LAGUNA v3 🐕🐈🐇🐦🐢")
print("     Works for dogs, cats, rabbits, birds, hamsters — any pet!")
print("     Biggest factor: Posting on Facebook = much higher chance!")
print("     Population ~57,776 | 17 Barangays | Community-focused")
print("="*85)

# Example with a rabbit
print("\nExample (for a rabbit):")
ex_result = predict_reunion(1.5, 3, 'Pansol', True, True)
print("→ 1.5-year-old rabbit, missing 3 days in Pansol, near water, POSTED ON FB")
print(f"   ✅ {ex_result}\n")

# Interactive loop — simplified, no pet type question
while True:
    print("Enter your lost pet details (or type 'quit' to exit):")
    
    try:
        age_input = input("\nAge in years (e.g. 2, 1.5, 0.5): ").strip()
        if age_input.lower() == 'quit':
            break
        if age_input == "":
            print("   ❌ Age is required.")
            continue
        age = float(age_input)

        days_input = input("Days missing: ").strip()
        if days_input == "":
            print("   ❌ Days missing is required.")
            continue
        days = int(days_input)

        barangay = input("Barangay (e.g. Pansol, Labuin, Aplaya, Bukal): ").strip()
        if barangay == "":
            print("   ❌ Barangay is required.")
            continue

        near_water_input = input("Near Laguna de Bay (water area)? (yes/no/oo): ").strip().lower()
        near_water = near_water_input in ['yes', 'y', 'oo']

        fb_input = input("Already posted on Facebook or local groups? (yes/no/oo): ").strip().lower()
        posted_on_fb = fb_input in ['yes', 'y', 'oo']

        result = predict_reunion(age, days, barangay, near_water, posted_on_fb)
        
        if result.startswith("Error"):
            print(f"\n   ❌ {result}")
            continue
            
        print(f"\n✅ {result}")

        # Personalized advice
        if "Likely" in result:
            print("   🎉 Good chance of reunion!")
            if posted_on_fb:
                print("   👏 Salamat sa pag-post sa FB — malaking tulong 'yan!")
            print("   💡 Next: Maglagay ng flyers sa plaza, magtanong sa kapitbahay,")
            print("      hanapin sa nearby barangays.")
        else:
            if not posted_on_fb:
                print("   ⚠️  POST ON FACEBOOK AGAD — malaki ang magiging difference!")
            print("   💡 Huwag mawalan ng pag-asa! Keep sharing daily sa groups.")

        print("\n   Recommended: Pila Laguna Residents & Missing Pets Philippines 🐾")

    except ValueError:
        print("   ❌ Please enter numbers only for age and days missing.")
    except Exception as e:
        print(f"   ❌ Something went wrong: {str(e)}. Try again.")

    print("\n" + "-"*60 + "\n")

print("\nSalamat po sa paggamit! Ingat sa inyong alaga. 🐾")
print("   Always post lost pets online — it really works in Pila!")