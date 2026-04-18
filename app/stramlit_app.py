import streamlit as st

st.set_page_config(
    page_title="Credit Rating System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Credit Rating System")
st.subheader("Hybrid TCN-Attention + XGBoost Credit Scoring")

st.markdown(
    """
Welcome. Use the sidebar to navigate through:
- Overview
- Model Performance
- Borrower Risk Scoring
- Portfolio Segmentation
- Watchlist
"""
)