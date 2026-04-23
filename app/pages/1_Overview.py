import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

import streamlit as st
import pandas as pd
import plotly.express as px

from utils import load_data_objects, format_pct, format_pd

st.title("📊 Executive Overview")

data = load_data_objects()

exec_summary = data["executive_summary"].copy()
grade_summary = data["credit_grade_summary"].copy()
decision_summary = data["decision_grade_summary"].copy()

# Safety cast
grade_summary["credit_grade"] = grade_summary["credit_grade"].astype(str)
decision_summary["decision_recommendation"] = decision_summary["decision_recommendation"].astype(str)

summary = exec_summary.iloc[0]

# =========================
# KPI SECTION
# =========================
st.subheader("Key Portfolio Metrics")

k1, k2, k3, k4 = st.columns(4)

k1.metric("Portfolio Avg PD", format_pd(summary["portfolio_avg_calibrated_pd"]))
k2.metric("High Risk Exposure (B/C/D)", format_pct(summary["high_risk_exposure"]))
k3.metric("Approval Rate", format_pct(summary["approval_rate"]))
k4.metric("Observed Default Rate", format_pct(summary["observed_default_rate"]))

# =========================
# DISTRIBUTION SECTION
# =========================
st.subheader("Portfolio Distribution")

col1, col2 = st.columns(2)

fig_grade = px.bar(
    grade_summary,
    x="credit_grade",
    y="borrower_count",
    title="Borrower Distribution by Credit Grade"
)
col1.plotly_chart(fig_grade, use_container_width=True, key="overview_grade_distribution")

fig_decision = px.pie(
    decision_summary,
    names="decision_recommendation",
    values="borrower_count",
    title="Decision Distribution"
)
col2.plotly_chart(fig_decision, use_container_width=True, key="overview_decision_distribution")

# =========================
# RISK ANALYSIS
# =========================
st.subheader("Risk Analysis")

col3, col4 = st.columns(2)

fig_avg_pd = px.bar(
    grade_summary,
    x="credit_grade",
    y="avg_predicted_pd",
    title="Average Predicted PD by Grade"
)
col3.plotly_chart(fig_avg_pd, use_container_width=True, key="overview_avg_pd")

fig_odr = px.bar(
    grade_summary,
    x="credit_grade",
    y="observed_default_rate",
    title="Observed Default Rate by Grade"
)
col4.plotly_chart(fig_odr, use_container_width=True, key="overview_odr")

# GAP ANALYSIS
st.subheader("Calibration Gap (Observed vs Predicted)")

grade_summary["gap"] = grade_summary["observed_default_rate"] - grade_summary["avg_predicted_pd"]

fig_gap = px.bar(
    grade_summary,
    x="credit_grade",
    y="gap",
    title="Calibration Gap by Grade"
)
st.plotly_chart(fig_gap, use_container_width=True, key="overview_gap")
