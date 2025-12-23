import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

print("Retraining with new feature: Posted on Facebook...\n")

np.random.seed(42)
n_samples = 500

barangays = [
    'Aplaya', 'Bagong Pook', 'Bukal', 'Bulilan Norte', 'Bulilan Sur',
    'Concepcion', 'Labuin', 'Linga', 'Masico', 'Mojon', 'Pansol',
    'Pinagbayanan', 'San Antonio', 'San Miguel', 'Santa Clara Norte',
    'Santa Clara Sur', 'Tubuan'
]

pet_types = ['Dog (Aspin)', 'Dog (Purebred)', 'Cat (Puspin)', 'Cat (Purebred)']

data = {
    'pet_type': np.random.choice(pet_types, size=n_samples),
    'age_years': np.round(np.random.uniform(0.5, 15, size=n_samples), 1),
    'days_missing': np.random.randint(1, 60, size=n_samples),
    'barangay': np.random.choice(barangays, size=n_samples),
    'near_water': np.random.choice([True, False], size=n_samples, p=[0.4, 0.6]),
    'posted_on_fb': np.random.choice([True, False], size=n_samples, p=[0.6, 0.4]),  # 60% posted
    'found': np.random.binomial(1, p=0.50, size=n_samples)
}

df = pd.DataFrame(data)

# Strong realistic patterns
df.loc[df['days_missing'] < 7, 'found'] = 1
df.loc[df['days_missing'] > 30, 'found'] = 0
df.loc[df['posted_on_fb'] == True, 'found'] = np.random.choice([1, 0], size=len(df[df['posted_on_fb']]), p=[0.85, 0.15])  # Big boost
purebred_mask = df['pet_type'].str.contains('Purebred')
df.loc[purebred_mask, 'found'] = np.random.choice([1, 0], size=purebred_mask.sum(), p=[0.65, 0.35])

df.to_csv('lost_pets_pila_dataset.csv', index=False)

# Preprocess
le_pet = LabelEncoder()
le_barangay = LabelEncoder()

df['pet_type_encoded'] = le_pet.fit_transform(df['pet_type'])
df['barangay_encoded'] = le_barangay.fit_transform(df['barangay'])

features = ['age_years', 'days_missing', 'near_water', 'posted_on_fb',
            'pet_type_encoded', 'barangay_encoded']

X = df[features]
y = df['found']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print(f"New Accuracy: {accuracy_score(model.predict(X_test), y_test):.2%}")

joblib.dump(model, 'lost_pet_model.pkl')
joblib.dump(le_pet, 'le_pet.pkl')
joblib.dump(le_barangay, 'le_barangay.pkl')
print("\nRetrained with Facebook post feature! Model saved.")

input("\nPress Enter to close...")