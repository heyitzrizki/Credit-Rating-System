import pandas as pd
import streamlit as st

st.title("Model Performance")

perf_df = pd.DataFrame(
    {
        "Metric": ["Valid ROC-AUC", "Test ROC-AUC", "Valid PR-AUC", "Test PR-AUC"],
        "Benchmark Static-Only": [0.7178, 0.7172, 0.1872, 0.2134],
        "Final Hybrid": [0.7233, 0.7273, 0.2137, 0.2256],
    }
)

st.dataframe(perf_df, use_container_width=True)

cal_df = pd.DataFrame(
    {
        "Model": ["Benchmark Static-Only", "Final Hybrid Raw", "Final Hybrid Platt-Calibrated"],
        "Test Brier": [0.1672, 0.1671, 0.0683],
        "Test ECE": [0.2710, 0.2770, 0.0161],
    }
)

st.markdown("### Calibration summary")
st.dataframe(cal_df, use_container_width=True)