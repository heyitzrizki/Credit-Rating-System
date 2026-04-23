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
```bash
Credit-Rating-System/
│
├── app/
│   ├── streamlit_app.py
│   ├── utils.py
│   ├── model_utils.py
│   └── pages/
│       ├── 1_Overview.py
│       ├── 2_Model_Performance.py
│       ├── 3_Borrower_Risk_Scoring.py
│       ├── 4_Portfolio_Segmentation.py
│       └── 5_Watchlist.py
│
├── artifacts/
│   ├── model files (.joblib, .pt)
│   ├── processed datasets (.csv)
│   └── SHAP outputs
│
├── notebooks/
│   └── credit_rating_final.ipynb
│
└── requirements.txt
```

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

```text
Raw Data
   ↓
Feature Engineering
   ↓
Static + Temporal Feature Construction
   ↓
Missing Value Handling & Encoding
   ↓
Feature Alignment
   ↓
TCN Embedding Generation
   ↓
Model Training (XGBoost)
   ↓
Probability Calibration (Platt Scaling)
   ↓
Artifact Generation
```

---

## 📈 Explainability

- **SHAP (Global & Local)**  
  Provides both portfolio-level and borrower-level interpretability  

- **Feature Importance Ranking**  
  Identifies key drivers of credit risk  

- **Individual Borrower Explanations**  
  Explains why a borrower is classified as high or low risk  

- **Temporal Attention Analysis**  
  Highlights critical time periods influencing model decisions  

---

## 🧪 Model Evaluation

**Metrics Used:**
- ROC-AUC  
- PR-AUC  
- Brier Score  
- Expected Calibration Error (ECE)  

**Evaluation Focus:**
- Emphasis on **probability calibration**
- Prioritizes **business usability over raw predictive accuracy**

---

## 🧩 Design Philosophy

This system is designed to reflect real-world credit risk environments:

- **Layered Architecture**
  - Data Layer  
  - Model Layer  
  - UI Layer  

- **Production-Oriented Design**
  - Scalable for deployment  
  - Modular for future model upgrades  

- **Business-Centric Approach**
  - Interpretability over black-box performance  
  - Decision support over pure prediction  

---

## ⚠️ Limitations

- Large SHAP dataset (~70MB) may impact deployment performance  
- No real-time API (currently batch-based processing)  
- Assumes structured and pre-cleaned financial data  

---

## 🔮 Future Improvements

- Model monitoring & drift detection  
- Real-time scoring API  
- Automated retraining pipeline  
- Scenario simulation for credit policy testing  

---

## 👤 Author

**Rizki Anwar**  
Business Analytics & Machine Learning  

---

## 📌 Notes

This project is intended for:

- Learning purposes  
- Portfolio demonstration  
- Simulation of real-world credit scoring systems  
