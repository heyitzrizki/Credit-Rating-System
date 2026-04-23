import pandas as pd
import streamlit as st

from utils import (
    assign_credit_grade_from_summary,
    assign_decision_from_grade,
    build_existing_borrower_sequence,
    build_temporal_preset,
    get_tcn_embedding,
    load_data_objects,
    load_models,
    preprocess_static_row,
    score_borrower,
)

st.set_page_config(page_title="Borrower Rating & Decisioning", layout="wide")

xgb_model, platt, encoder, _ = load_models()
data = load_data_objects()

risk_table = data["risk_table"].copy()
grade_summary = data["credit_grade_summary"].copy()
borrower_profile_ui = data["borrower_profile_ui"].copy()
borrower_explanation_summary = data.get("borrower_explanation_summary", pd.DataFrame())

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1400px;
        }
        .section-card {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 1.1rem 1.15rem 0.95rem 1.15rem;
            margin-bottom: 1rem;
        }
        .section-title {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.55rem;
        }
        .muted {
            color: #B7BFCA;
            font-size: 0.96rem;
            line-height: 1.65;
        }
        .profile-label {
            color: #97A1AE;
            font-size: 0.85rem;
            margin-bottom: 0.15rem;
        }
        .profile-value {
            font-size: 1.02rem;
            font-weight: 600;
            margin-bottom: 0.8rem;
        }
        .pill {
            display: inline-block;
            padding: 0.38rem 0.72rem;
            border-radius: 999px;
            margin-right: 0.45rem;
            margin-bottom: 0.4rem;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.08);
            font-size: 0.9rem;
            color: #D9DEE7;
        }
        .footnote-box {
            background: rgba(255,255,255,0.03);
            border-left: 4px solid rgba(255,255,255,0.22);
            border-radius: 10px;
            padding: 0.9rem 1rem;
            margin-top: 0.5rem;
            margin-bottom: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Borrower Rating & Decisioning")
st.caption("Individual borrower assessment with rating, decision recommendation, and explanation support")

mode = st.radio("Scoring Mode", ["Existing Borrower", "Manual Simulation"], horizontal=True)

# Helper functions for UI
def fmt_currency(x):
    if pd.isna(x):
        return "-"
    return f"{x:,.0f}"

def fmt_num(x, digits=4):
    if pd.isna(x):
        return "-"
    return f"{x:.{digits}f}"

def fmt_pct(x, digits=1):
    if pd.isna(x):
        return "-"
    return f"{x * 100:.{digits}f}%"

def grade_group_label(grade: str) -> str:
    if grade in ["AAA", "AA", "A"]:
        return "Investment Grade"
    elif grade in ["BBB", "BB"]:
        return "Review Grade"
    return "High Risk"

def render_profile_card(profile_row: pd.Series):
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown('<div class="section-card"><div class="section-title">Identity & Application</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Borrower ID</div><div class="profile-value">{profile_row.get("SK_ID_CURR", "-")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Contract Type</div><div class="profile-value">{profile_row.get("NAME_CONTRACT_TYPE", "-")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Gender</div><div class="profile-value">{profile_row.get("CODE_GENDER", "-")}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-card"><div class="section-title">Financial Profile</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Income</div><div class="profile-value">{fmt_currency(profile_row.get("AMT_INCOME_TOTAL"))}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Credit Amount</div><div class="profile-value">{fmt_currency(profile_row.get("AMT_CREDIT"))}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Annuity</div><div class="profile-value">{fmt_currency(profile_row.get("AMT_ANNUITY"))}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Goods Price</div><div class="profile-value">{fmt_currency(profile_row.get("AMT_GOODS_PRICE"))}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="section-card"><div class="section-title">Household & Stability</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Family Status</div><div class="profile-value">{profile_row.get("NAME_FAMILY_STATUS", "-")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Children</div><div class="profile-value">{profile_row.get("CNT_CHILDREN", "-")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Own Car</div><div class="profile-value">{profile_row.get("FLAG_OWN_CAR", "-")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Own Realty</div><div class="profile-value">{profile_row.get("FLAG_OWN_REALTY", "-")}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="section-card"><div class="section-title">External Risk Signals</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">EXT_SOURCE_1</div><div class="profile-value">{fmt_num(profile_row.get("EXT_SOURCE_1"), 3)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">EXT_SOURCE_2</div><div class="profile-value">{fmt_num(profile_row.get("EXT_SOURCE_2"), 3)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">EXT_SOURCE_3</div><div class="profile-value">{fmt_num(profile_row.get("EXT_SOURCE_3"), 3)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Employment Length (days)</div><div class="profile-value">{fmt_currency(profile_row.get("DAYS_EMPLOYED"))}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

def render_explanation_block(sk_id):
    if borrower_explanation_summary.empty:
        st.info("Borrower explanation summary is not available yet.")
        return

    explain_row = borrower_explanation_summary[
        borrower_explanation_summary["SK_ID_CURR"] == sk_id
    ]

    if explain_row.empty:
        st.info("No borrower-level explanation summary found for this borrower.")
        return

    explain_row = explain_row.iloc[0]

    e1, e2 = st.columns(2)

    with e1:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">Top Factors Increasing Risk</div>
            """,
            unsafe_allow_html=True,
        )
        for col in ["top_1_risk_driver", "top_2_risk_driver", "top_3_risk_driver"]:
            val = explain_row.get(col, None)
            if pd.notna(val) and val is not None:
                st.markdown(f'<span class="pill">{val}</span>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with e2:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">Top Factors Reducing Risk</div>
            """,
            unsafe_allow_html=True,
        )
        for col in ["top_1_support_driver", "top_2_support_driver", "top_3_support_driver"]:
            val = explain_row.get(col, None)
            if pd.notna(val) and val is not None:
                st.markdown(f'<span class="pill">{val}</span>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Existing Borrower Mode
if mode == "Existing Borrower":
    borrower_options = borrower_profile_ui["SK_ID_CURR"].tolist()
    selected_borrower = st.selectbox("Select borrower ID", borrower_options)

    borrower_row_full = data["app_static"][data["app_static"]["SK_ID_CURR"] == selected_borrower].copy()
    borrower_profile_row = borrower_profile_ui[borrower_profile_ui["SK_ID_CURR"] == selected_borrower].copy()

    if borrower_profile_row.empty:
        st.error("Borrower profile not found.")
        st.stop()

    borrower_profile_row = borrower_profile_row.iloc[0]

    static_raw = borrower_row_full.drop(columns=[c for c in ["SK_ID_CURR", "TARGET"] if c in borrower_row_full.columns])
    static_processed = preprocess_static_row(static_raw, data)

    seq, mask = build_existing_borrower_sequence(selected_borrower, data)
    embedding, attn = get_tcn_embedding(encoder, seq, mask)
    raw_pd, calibrated_pd = score_borrower(static_processed, embedding, xgb_model, platt, data["emb_cols_v2"])

    credit_grade = assign_credit_grade_from_summary(calibrated_pd, grade_summary)
    decision = assign_decision_from_grade(credit_grade)
    grade_group = grade_group_label(credit_grade)

    borrower_rank_row = risk_table[risk_table["SK_ID_CURR"] == selected_borrower]
    portfolio_percentile = borrower_rank_row["portfolio_percentile"].iloc[0] if not borrower_rank_row.empty and "portfolio_percentile" in borrower_rank_row.columns else None
    actual_default = borrower_rank_row["actual_default"].iloc[0] if not borrower_rank_row.empty and "actual_default" in borrower_rank_row.columns else None

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Raw PD", f"{raw_pd:.4f}")
    m2.metric("Calibrated PD", f"{calibrated_pd:.4f}")
    m3.metric("Credit Grade", credit_grade)
    m4.metric("Decision", decision)
    m5.metric("Portfolio Percentile", fmt_pct(portfolio_percentile, 1) if portfolio_percentile is not None else "-")

    st.markdown(
        """
        <div class="footnote-box">
            <b>How to read these values:</b><br>
            <b>Raw PD</b> is the direct probability of default produced by the model.<br>
            <b>Calibrated PD</b> is the adjusted probability used by the system for rating and decision recommendation.
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns((1.1, 1))
    with left:
        st.markdown("### Decision Summary")
        st.markdown(
            f"""
            <div class="section-card">
                <div class="section-title">Borrower Assessment</div>
                <div class="muted">
                    This borrower is currently assigned to <b>{credit_grade}</b>, which falls under the
                    <b>{grade_group}</b> segment. Based on the calibrated PD, the recommended decision is
                    <b>{decision}</b>.
                    {"<br><br>Observed default label in test data: <b>" + str(actual_default) + "</b>." if actual_default is not None else ""}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown("### Policy Reference")
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">Grade-to-Decision Mapping</div>
                <div class="muted">
                    AAA–A → <b>Approve</b><br>
                    BBB–BB → <b>Review</b><br>
                    B–D → <b>Reject</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Borrower Profile")
    render_profile_card(borrower_profile_row)

    st.markdown("### Explanation Support")
    render_explanation_block(selected_borrower)

    with st.expander("Show temporal attention weights"):
        attn_df = pd.DataFrame(
            {
                "time_step": list(range(1, len(attn) + 1)),
                "attention_weight": attn,
            }
        )
        st.dataframe(attn_df, use_container_width=True, hide_index=True)

# Manual Simulation Mode
else:
    st.markdown("### Manual Simulation")
    st.caption("Modify a borrower template and test how the system responds under different borrower and temporal conditions.")

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

        credit_grade = assign_credit_grade_from_summary(calibrated_pd, grade_summary)
        decision = assign_decision_from_grade(credit_grade)
        grade_group = grade_group_label(credit_grade)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Raw PD", f"{raw_pd:.4f}")
        m2.metric("Calibrated PD", f"{calibrated_pd:.4f}")
        m3.metric("Credit Grade", credit_grade)
        m4.metric("Decision", decision)

        st.markdown(
            """
            <div class="footnote-box">
                <b>Interpretation note:</b><br>
                The calibrated PD is the probability used for grade assignment and decision recommendation.
                Manual simulation is useful for scenario testing, not for replacing full borrower due diligence.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Simulated Assessment")
        st.markdown(
            f"""
            <div class="section-card">
                <div class="section-title">Simulation Result</div>
                <div class="muted">
                    Under the selected borrower inputs and temporal preset <b>{preset}</b>, the borrower is
                    assigned to grade <b>{credit_grade}</b>, which belongs to the <b>{grade_group}</b> segment.
                    The recommended decision is <b>{decision}</b>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("Show edited borrower inputs"):
            st.dataframe(edited_row, use_container_width=True, hide_index=True)