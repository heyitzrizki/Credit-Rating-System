# 📊 Credit Rating System  
### Hybrid TCN-Attention + XGBoost for Credit Risk Scoring

---

## 🚀 Overview

This project is an **end-to-end credit risk modeling system** that combines:

- Deep temporal learning (TCN + Attention)
- Gradient boosting (XGBoost)
- Probability calibration (Platt Scaling)
- Explainability (SHAP + Temporal Attention)
- Interactive deployment (Streamlit dashboard)

The system is designed to **simulate real-world credit scoring pipelines** used in financial institutions, supporting both:
- **Risk assessment**
- **Decision-making**
- **Portfolio monitoring**

---

## 💡 Key Objectives

- Predict borrower **probability of default (PD)**
- Translate model output into **business decisions (Approve / Review / Reject)**
- Provide **interpretable explanations** for stakeholders
- Enable **portfolio-level risk monitoring**

---

## 🧠 Model Architecture

### Hybrid Model
Temporal Data → TCN + Attention → Embedding
↓
Static Features → Feature Engineering → XGBoost → PD (raw)
↓
Platt Scaling
↓
Calibrated PD


### Components

| Component | Purpose |
|----------|--------|
| TCN (Temporal Convolutional Network) | Captures time-dependent borrower behavior |
| Attention Layer | Identifies important time periods |
| XGBoost | Final risk prediction model |
| Platt Scaling | Probability calibration |
| SHAP | Feature-level explainability |

---

## 📊 Features

### 1. Executive Dashboard
- Portfolio average PD
- Risk exposure (B/C/D grades)
- Approval rate
- Calibration gap analysis

### 2. Borrower Risk Scoring
- Individual PD prediction
- Credit grade assignment (AAA → D)
- Decision recommendation
- Borrower profile UI
- Explainability:
  - SHAP (feature impact)
  - Temporal attention weights

### 3. Portfolio Segmentation
- Risk distribution by grade
- Default rate comparison
- Policy evaluation

### 4. Watchlist Monitoring
- High-risk borrower detection
- Threshold-based filtering
- Risk distribution visualization

---

## 🧾 Credit Rating System

### Grade Mapping

| Grade | Risk Level | Decision |
|------|------------|---------|
| AAA | Very Low | Approve |
| AA | Low | Approve |
| A | Moderate | Approve |
| BBB | Medium | Review |
| BB | Elevated | Review |
| B | High | Reject |
| C | Very High | Reject |
| D | Default | Reject |

---

## 📦 Project Structure
Credit-Rating-System/
│
├── app/
│ ├── streamlit_app.py
│ ├── utils.py
│ ├── model_utils.py
│ └── pages/
│ ├── 1_Overview.py
│ ├── 2_Model_Performance.py
│ ├── 3_Borrower_Risk_Scoring.py
│ ├── 4_Portfolio_Segmentation.py
│ └── 5_Watchlist.py
│
├── artifacts/
│ ├── model files (.joblib, .pt)
│ ├── processed datasets (.csv)
│ └── SHAP outputs
│
├── notebooks/
│ └── credit_rating_final.ipynb
│
└── requirements.txt


---

## ⚙️ Installation

```bash
git clone https://github.com/your-username/Credit-Rating-System.git
cd Credit-Rating-System
pip install -r requirements.txt
```
## ▶️ Run the App
streamlit run app/streamlit_app.py

## 📊 Data Pipeline
Raw data → Feature engineering
Static + Temporal features
Missing value handling
Encoding + alignment
TCN embedding generation
Model training (XGBoost)
Calibration (Platt scaling)
Artifact generation

## 📈 Explainability
SHAP (Global + Local)
Feature importance ranking
Individual borrower explanations
Temporal Attention
Highlights critical time periods influencing risk

## 🧪 Model Evaluation

Metrics used:

ROC-AUC
PR-AUC
Brier Score
Expected Calibration Error (ECE)

Focus:

Probability calibration and business usability over raw accuracy

## 🧩 Design Philosophy

This system is built to reflect:

Real-world credit risk pipelines
Separation between:
data layer
model layer
UI layer
Scalability for:
production deployment
future model upgrades

## ⚠️ Limitations
Large SHAP file (~70MB) may impact deployment performance
No real-time API integration (batch-based system)
Assumes clean structured financial data

## 🔮 Future Improvements
Model monitoring (drift detection)
Real-time scoring API
Automated retraining pipeline
Scenario simulation for credit policy testing

## 👤 Author

Rizki Anwar
Business Analytics & Machine Learning

## 📌 Notes

This project is intended for:

learning purposes
portfolio demonstration
simulation of real-world credit scoring systems
