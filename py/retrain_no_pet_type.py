import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

print("Retraining WITHOUT pet_type — works for ANY pet now!\n")

# Load the latest dataset (with posted_on_fb)
df = pd.read_csv('lost_pets_pila_dataset.csv')

# Keep realistic patterns (no pet_type boost needed)
df.loc[df['days_missing'] < 7, 'found'] = 1
df.loc[df['days_missing'] > 30, 'found'] = 0
df.loc[df['posted_on_fb'] == True, 'found'] = np.random.choice([1, 0], size=len(df[df['posted_on_fb']]), p=[0.85, 0.15])

# Encode only barangay now
le_barangay = LabelEncoder()
df['barangay_encoded'] = le_barangay.fit_transform(df['barangay'])

# New features — NO pet_type
features = ['age_years', 'days_missing', 'near_water', 'posted_on_fb', 'barangay_encoded']

X = df[features]
y = df['found']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print(f"New Accuracy: {accuracy_score(y_test, model.predict(X_test)):.2%}")
print("Feature Importance:")
print(pd.Series(model.feature_importances_, index=features).sort_values(ascending=False))

# Save new model (no pet encoder needed)
joblib.dump(model, 'lost_pet_model.pkl')
joblib.dump(le_barangay, 'le_barangay.pkl')
print("\nRetrained! Now works for rabbits, birds, any pet. Use updated main script.")

input("\nPress Enter to exit...")