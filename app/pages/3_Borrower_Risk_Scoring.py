import pandas as pd
import streamlit as st
from utils import (
    assign_decision_band,
    assign_risk_band,
    build_existing_borrower_sequence,
    build_temporal_preset,
    get_tcn_embedding,
    load_data_objects,
    load_models,
    preprocess_static_row,
    score_borrower,
)

xgb_model, platt, encoder, _ = load_models()
data = load_data_objects()

st.title("Borrower Risk Scoring")

mode = st.radio("Scoring Mode", ["Existing Borrower", "Manual Simulation"], horizontal=True)

if mode == "Existing Borrower":
    app_static = data["app_static"]
    borrower_options = app_static["SK_ID_CURR"].tolist()
    selected_borrower = st.selectbox("Select borrower ID", borrower_options)

    borrower_row = app_static[app_static["SK_ID_CURR"] == selected_borrower].copy()
    static_raw = borrower_row.drop(columns=[c for c in ["SK_ID_CURR", "TARGET"] if c in borrower_row.columns])
    static_processed = preprocess_static_row(static_raw, data)

    seq, mask = build_existing_borrower_sequence(selected_borrower, data)
    embedding, attn = get_tcn_embedding(encoder, seq, mask)
    raw_pd, calibrated_pd = score_borrower(static_processed, embedding, xgb_model, platt, data["emb_cols_v2"])

    band_summary = data["risk_band_summary"]
    risk_band = assign_risk_band(calibrated_pd, band_summary)
    decision = assign_decision_band(risk_band)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Raw PD", f"{raw_pd:.4f}")
    c2.metric("Calibrated PD", f"{calibrated_pd:.4f}")
    c3.metric("Risk Band", risk_band)
    c4.metric("Decision", decision)

    st.markdown("### Borrower snapshot")
    st.dataframe(borrower_row.head(1), use_container_width=True)

else:
    st.markdown("### Manual Simulation")
    app_static = data["app_static"]
    template_id = st.selectbox("Base borrower template", app_static["SK_ID_CURR"].tolist())
    template_row = app_static[app_static["SK_ID_CURR"] == template_id].copy().iloc[[0]]

    editable_numeric = [
        c for c in [
            "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY",
            "AMT_GOODS_PRICE", "CNT_CHILDREN", "DAYS_BIRTH", "DAYS_EMPLOYED"
        ] if c in template_row.columns
    ]
    editable_categorical = [
        c for c in [
            "CODE_GENDER", "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE",
            "FLAG_OWN_CAR", "FLAG_OWN_REALTY", "NAME_FAMILY_STATUS"
        ] if c in template_row.columns
    ]

    edited_row = template_row.copy()

    with st.form("manual_form"):
        cols = st.columns(2)
        for i, col in enumerate(editable_numeric):
            value = float(template_row.iloc[0][col]) if pd.notna(template_row.iloc[0][col]) else 0.0
            edited_row.at[edited_row.index[0], col] = cols[i % 2].number_input(col, value=value)

        for i, col in enumerate(editable_categorical):
            current = str(template_row.iloc[0][col]) if pd.notna(template_row.iloc[0][col]) else "Unknown"
            edited_row.at[edited_row.index[0], col] = cols[i % 2].text_input(col, value=current)

        preset = st.selectbox(
            "Temporal profile preset",
            ["Stable payer", "Mild deterioration", "High delinquency", "Recovering borrower"],
        )
        submitted = st.form_submit_button("Score borrower")

    if submitted:
        static_raw = edited_row.drop(columns=[c for c in ["SK_ID_CURR", "TARGET"] if c in edited_row.columns])
        static_processed = preprocess_static_row(static_raw, data)
        seq, mask = build_temporal_preset(data, preset)
        embedding, _ = get_tcn_embedding(encoder, seq, mask)
        raw_pd, calibrated_pd = score_borrower(static_processed, embedding, xgb_model, platt, data["emb_cols_v2"])

        band_summary = data["risk_band_summary"]
        risk_band = assign_risk_band(calibrated_pd, band_summary)
        decision = assign_decision_band(risk_band)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Raw PD", f"{raw_pd:.4f}")
        c2.metric("Calibrated PD", f"{calibrated_pd:.4f}")
        c3.metric("Risk Band", risk_band)
        c4.metric("Decision", decision)