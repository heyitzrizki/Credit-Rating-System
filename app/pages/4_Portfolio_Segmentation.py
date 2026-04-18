import streamlit as st
from utils import load_data_objects

data = load_data_objects()

st.title("Portfolio Segmentation")

st.markdown("### Risk band summary")
st.dataframe(data["risk_band_summary"], use_container_width=True)

st.markdown("### Decision band summary")
st.dataframe(data["decision_band_summary"], use_container_width=True)

st.markdown("### Threshold-based policy summary")
st.dataframe(data["threshold_policy_summary"], use_container_width=True)

band_df = data["risk_band_summary"].set_index("risk_band")
st.markdown("### Observed default rate by risk band")
st.bar_chart(band_df["observed_default_rate"])

decision_df = data["decision_band_summary"].set_index("decision_band")
st.markdown("### Portfolio share by decision band")
st.bar_chart(decision_df["share_of_portfolio"])