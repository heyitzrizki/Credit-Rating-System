import streamlit as st
from utils import load_data_objects

data = load_data_objects()
metadata = data["metadata"]

st.title("Executive Overview")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Test ROC-AUC", f"{metadata['test_roc_auc']:.4f}")
c2.metric("Test PR-AUC", f"{metadata['test_pr_auc']:.4f}")
c3.metric("Test Brier (Platt)", f"{metadata['test_brier_platt']:.4f}")
c4.metric("Calibration", metadata["calibration_method"])

st.markdown("### Final model")
st.write(metadata["final_model_name"])

st.markdown("### Key findings")
st.markdown(
    "- Hybrid model outperformed the static-only benchmark\n"
    "- SMOTE reduced PR-AUC and was excluded\n"
    "- Platt calibration improved PD reliability\n"
    "- The system supports risk banding and credit decision simulation"
)