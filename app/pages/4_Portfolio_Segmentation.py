import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

import streamlit as st
import pandas as pd
import plotly.express as px

from utils import load_data_objects, format_pct

st.title("📊 Portfolio Segmentation")

data = load_data_objects()

grade_summary = data["credit_grade_summary"].copy()
group_summary = data["grade_group_summary"].copy()
decision_summary = data["decision_grade_summary"].copy()
policy_summary = data["threshold_policy_summary"].copy()

# Safety cast
grade_summary["credit_grade"] = grade_summary["credit_grade"].astype(str)
group_summary["grade_group"] = group_summary["grade_group"].astype(str)
decision_summary["decision_recommendation"] = decision_summary["decision_recommendation"].astype(str)
policy_summary["decision_pd_threshold"] = policy_summary["decision_pd_threshold"].astype(str)

# =========================
# DISTRIBUTION
# =========================
st.subheader("Distribution")

col1, col2 = st.columns(2)

fig_grade = px.bar(
    grade_summary,
    x="credit_grade",
    y="borrower_count",
    title="Grade Distribution"
)
col1.plotly_chart(fig_grade, use_container_width=True, key="portfolio_grade_dist")

fig_group = px.pie(
    group_summary,
    names="grade_group",
    values="borrower_count",
    title="Grade Group Distribution"
)
col2.plotly_chart(fig_group, use_container_width=True, key="portfolio_group_dist")

# =========================
# RISK ANALYSIS
# =========================
st.subheader("Risk Analysis")

col3, col4 = st.columns(2)

fig_odr = px.bar(
    grade_summary,
    x="credit_grade",
    y="observed_default_rate",
    title="Observed Default Rate"
)
col3.plotly_chart(fig_odr, use_container_width=True, key="portfolio_odr")

fig_pd = px.bar(
    grade_summary,
    x="credit_grade",
    y="avg_predicted_pd",
    title="Predicted PD"
)
col4.plotly_chart(fig_pd, use_container_width=True, key="portfolio_pd")

# =========================
# DECISION DISTRIBUTION
# =========================
st.subheader("Decision Breakdown")

fig_decision = px.bar(
    decision_summary,
    x="decision_recommendation",
    y="borrower_count",
    title="Decision Count"
)
st.plotly_chart(fig_decision, use_container_width=True, key="portfolio_decision")

# =========================
# POLICY COMPARISON
# =========================
st.subheader("Policy Comparison")

fig_policy = px.bar(
    policy_summary,
    x="decision_pd_threshold",
    y="observed_default_rate",
    title="Observed Default Rate by Policy"
)
st.plotly_chart(fig_policy, use_container_width=True, key="portfolio_policy")
