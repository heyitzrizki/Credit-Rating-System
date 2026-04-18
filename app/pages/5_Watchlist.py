import streamlit as st
from utils import load_data_objects

data = load_data_objects()
risk_table = data["risk_table"]
top_high_risk = data["top_high_risk"]

st.title("High-Risk Watchlist")

top_n = st.slider("Number of borrowers to display", min_value=10, max_value=200, value=50, step=10)
st.dataframe(top_high_risk.head(top_n), use_container_width=True)

min_pd = st.slider("Minimum calibrated PD", min_value=0.0, max_value=1.0, value=0.10, step=0.01)
filtered = risk_table[risk_table["pd_calibrated"] >= min_pd].copy()

st.write(f"Borrowers above threshold: {len(filtered)}")
st.dataframe(filtered.sort_values("pd_calibrated", ascending=False), use_container_width=True)

if not filtered.empty:
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Calibrated PD", f"{filtered['pd_calibrated'].mean():.4f}")
    c2.metric("Observed Default Rate", f"{filtered['actual_default'].mean():.4f}")
    c3.metric("Portfolio Share", f"{len(filtered) / len(risk_table):.2%}")