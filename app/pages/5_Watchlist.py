import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

import streamlit as st
import pandas as pd
import plotly.express as px

from utils import load_data_objects, format_pd

st.title("🚨 High-Risk Watchlist")

data = load_data_objects()

risk_table = data["risk_table"]

# FILTER
threshold = st.slider("Minimum Calibrated PD", 0.0, 1.0, 0.10)

filtered = risk_table[risk_table["pd_calibrated"] >= threshold]

st.write(f"Borrowers above threshold: {len(filtered)}")

# TABLE
st.dataframe(filtered.head(50))

# DISTRIBUTION
st.subheader("Risk Distribution")

col1, col2 = st.columns(2)

fig_grade = px.histogram(
    filtered,
    x="credit_grade",
    title="Grade Distribution"
)
col1.plotly_chart(fig_grade, use_container_width=True, key="watchlist_grade")

fig_pd = px.histogram(
    filtered,
    x="pd_calibrated",
    nbins=30,
    title="PD Distribution"
)
col2.plotly_chart(fig_pd, use_container_width=True, key="watchlist_pd")
