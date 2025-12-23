# Lost Pet Reunion Predictor for Pila, Laguna 🐕🐈🐇🐦🐢

A machine learning project that predicts the likelihood of a lost pet being reunited with its owner in **Pila, Laguna, Philippines**.

This is version 4 (v4) — works for **any pet type** (dogs, cats, rabbits, birds, hamsters, etc.) by removing pet type as a feature and adding feature engineering (`days_missing_bucket`) to improve recall and reduce false negatives.

Now deployed as an interactive **public web app** for easy community use!

---

## v3 vs v4 Performance Summary

| Version | Accuracy | Recall (Found) | Notes                                           |
| ------- | -------- | -------------- | ----------------------------------------------- |
| v3      | 75.2%    | 83.2%          | Some false negatives (53); original features    |
| v4      | 100%     | 100%           | Added `days_missing_bucket`; zero false negatives |

---

## Project Progress (as of December 2025)

- **v1–v2**: Basic Random Forest model using pet type (Aspin, Puspin, Purebred), age, days missing, barangay, proximity to water, and microchip status.
- **v3 Improvements**:
  - Removed pet type feature (works universally for any pet).
  - Key factors: age, days missing, barangay, near water, and **posting on Facebook** (strongest predictor).
  - Added flexible barangay input handling.
  - Built interactive console version in Python.
- **v4 Feature Engineering**:
  - Added `days_missing_bucket` to capture non-linear recovery patterns in days missing.
  - Improved recall and F1-score for the “Found” class; zero false negatives on synthetic data.
- **Major Milestone**: Streamlit web app for public access.
  - Clean, mobile-friendly interface.
  - Real-time predictions with personalized advice (English + Filipino).
  - Encourages best practices: posting on FB, flyers, asking neighbors.
- Next steps: Collect real data from local reports/Facebook groups to retrain and improve accuracy.

---

## Features (v4 Web App)

- Predicts reunion probability based on:
  - Pet age (years)
  - Days missing
  - Barangay in Pila (all 17 supported)
  - Near Laguna de Bay/water area
  - Posted on Facebook/local groups (biggest impact!)
- Outputs probability percentage + "Likely/Unlikely Found"
- Personalized advice and encouragement
- Works for **any pet** — no need to specify type!
- Computes `days_missing_bucket` automatically from user input — seamless for users.

---

## Model Evaluation & Performance

Dataset: 500 synthetic samples

### v3 Performance (before feature engineering)
**Confusion Matrix**

[[114 71]
[ 53 262]]


| Class         | Precision | Recall    | F1-score  |
| ------------- | --------- | --------- | --------- |
| Not Found (0) | 0.683     | 0.616     | 0.648     |
| Found (1)     | 0.787     | 0.832     | 0.809     |

- **Overall accuracy:** 75.2%  
- **Recall for “Found” pets:** 83.2%  

---

### v4 Performance (with `days_missing_bucket`)
**Confusion Matrix**

[[185 0]
[ 0 315]]


| Class         | Precision | Recall | F1-score |
| ------------- | --------- | ------ | -------- |
| Not Found (0) | 1.000     | 1.000  | 1.000    |
| Found (1)     | 1.000     | 1.000  | 1.000    |

- **Overall accuracy:** 100%  
- **Recall for “Found” pets:** 100%  
- **Key improvement:** Zero false negatives — all pets likely to be found are correctly identified.

---

### Key Takeaways

- Feature engineering (`days_missing_bucket`) effectively captures non-linear patterns.
- Recall-focused improvements make the model **community-use friendly**.
- Streamlit app computes this feature automatically — users only need to enter days missing.

---

## Live Demo

Try it here:  
**[Lost Pet Reunion Predictor Web App](https://your-app-name.streamlit.app)**  
*(Replace with your deployed URL once live)*

Anyone in Pila (or nearby) can use it directly on their phone — just enter details and get an instant prediction 🐾

---

## How to Run Locally

1. Clone the repository or download the files.
2. Install dependencies:

```bash
pip install streamlit pandas scikit-learn joblib
3. Run the app: streamlit run app.py
4. Enjoy instant predictions for lost pets in Pila, Laguna!