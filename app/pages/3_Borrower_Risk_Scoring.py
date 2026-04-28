import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))
import pandas as pd
import streamlit as st

from utils import (
    assign_credit_grade_from_summary,
    assign_decision_from_grade,
<<<<<<< HEAD
    load_data_objects,
)

from model_utils import (
=======
    assign_grade_group,
>>>>>>> 25e2c74 (Update web streamlit)
    build_existing_borrower_sequence,
    build_temporal_preset,
    format_currency,
    format_pct,
    get_tcn_embedding,
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
portfolio_ecl = data.get("portfolio_ecl_base", pd.DataFrame())

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
st.caption(
    "Assess an individual borrower using estimated default risk, credit grade, recommendation, and main risk drivers."
)

mode = st.radio(
    "Choose scoring mode",
    ["Existing Borrower", "Manual Simulation"],
    horizontal=True,
    help=(
        "Existing Borrower uses borrowers already available in the test portfolio. "
        "Manual Simulation lets you modify a borrower profile and test the system response."
    ),
)


# Helper functions

def fmt_num(x, digits=2):
    if pd.isna(x):
        return "-"
    return f"{x:.{digits}f}"


def years_from_negative_days(x):
    if pd.isna(x):
        return None
    return abs(float(x)) / 365.25


def negative_days_from_years(x):
    if pd.isna(x):
        return None
    return -int(float(x) * 365.25)


def yes_no_to_flag(label):
    return "Y" if label == "Yes" else "N"


def flag_to_yes_no(value):
    return "Yes" if str(value).upper() == "Y" else "No"


def render_profile_card(profile_row: pd.Series):
    age = years_from_negative_days(profile_row.get("DAYS_BIRTH"))
    employment_years = years_from_negative_days(profile_row.get("DAYS_EMPLOYED"))

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown('<div class="section-card"><div class="section-title">Identity & Application</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Borrower ID</div><div class="profile-value">{profile_row.get("SK_ID_CURR", "-")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Contract Type</div><div class="profile-value">{profile_row.get("NAME_CONTRACT_TYPE", "-")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Gender</div><div class="profile-value">{profile_row.get("CODE_GENDER", "-")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Age</div><div class="profile-value">{fmt_num(age, 1)} years</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-card"><div class="section-title">Financial Profile</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Income</div><div class="profile-value">{format_currency(profile_row.get("AMT_INCOME_TOTAL"))}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Credit Amount</div><div class="profile-value">{format_currency(profile_row.get("AMT_CREDIT"))}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Annuity</div><div class="profile-value">{format_currency(profile_row.get("AMT_ANNUITY"))}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Goods Price</div><div class="profile-value">{format_currency(profile_row.get("AMT_GOODS_PRICE"))}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="section-card"><div class="section-title">Household & Stability</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Family Status</div><div class="profile-value">{profile_row.get("NAME_FAMILY_STATUS", "-")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Children</div><div class="profile-value">{profile_row.get("CNT_CHILDREN", "-")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Own Car</div><div class="profile-value">{flag_to_yes_no(profile_row.get("FLAG_OWN_CAR", "N"))}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Own Realty</div><div class="profile-value">{flag_to_yes_no(profile_row.get("FLAG_OWN_REALTY", "N"))}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="section-card"><div class="section-title">External Risk Signals</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">External Score 1</div><div class="profile-value">{fmt_num(profile_row.get("EXT_SOURCE_1"), 3)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">External Score 2</div><div class="profile-value">{fmt_num(profile_row.get("EXT_SOURCE_2"), 3)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">External Score 3</div><div class="profile-value">{fmt_num(profile_row.get("EXT_SOURCE_3"), 3)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">Employment Length</div><div class="profile-value">{fmt_num(employment_years, 1)} years</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_explanation_block(sk_id):
    st.markdown("### Main Risk Drivers")

    st.markdown(
        """
        <div class="footnote-box">
            This section summarizes the borrower-level factors that most increased or reduced the model's
            estimated default risk. These drivers are explanation support only and should not be interpreted
            as causal proof.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if borrower_explanation_summary.empty:
        st.info("Main risk driver explanation is not available for this deployment artifact.")
        return

    explain_row = borrower_explanation_summary[
        borrower_explanation_summary["SK_ID_CURR"] == sk_id
    ]

    if explain_row.empty:
        st.info(
            "No borrower-level explanation summary was generated for this borrower. "
            "The rating and recommendation are still available, but detailed driver analysis is unavailable."
        )
        return

    explain_row = explain_row.iloc[0]

    e1, e2 = st.columns(2)

    with e1:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">Factors Increasing Risk</div>
                <div class="muted">These variables pushed the borrower toward a higher estimated default risk.</div><br>
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
                <div class="section-title">Factors Reducing Risk</div>
                <div class="muted">These variables helped reduce the borrower's estimated default risk.</div><br>
            """,
            unsafe_allow_html=True,
        )
        for col in ["top_1_support_driver", "top_2_support_driver", "top_3_support_driver"]:
            val = explain_row.get(col, None)
            if pd.notna(val) and val is not None:
                st.markdown(f'<span class="pill">{val}</span>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_ecl_metrics(sk_id):
    if portfolio_ecl.empty:
        return

    borrower_ecl_row = portfolio_ecl[portfolio_ecl["SK_ID_CURR"] == sk_id]

    if borrower_ecl_row.empty:
        return

    borrower_ecl_row = borrower_ecl_row.iloc[0]

    st.markdown("### Expected Loss View")

    e1, e2, e3 = st.columns(3)
    e1.metric("Loss Severity Assumption", format_pct(borrower_ecl_row.get("LGD"), 1))
    e2.metric("Credit Exposure", format_currency(borrower_ecl_row.get("EAD")))
    e3.metric("Base Expected Loss", format_currency(borrower_ecl_row.get("ECL_base")))

    st.caption(
        "Expected loss is calculated as Estimated Default Risk × Loss Severity Assumption × Credit Exposure."
    )


def render_result_summary(raw_pd, calibrated_pd, credit_grade, decision, grade_group, actual_default=None):
    m1, m2, m3, m4, m5 = st.columns(5)

    m1.metric("Model Risk Score", f"{raw_pd:.4f}")
    m2.metric("Estimated Default Risk", f"{calibrated_pd:.4f}")
    m3.metric("Credit Grade", credit_grade)
    m4.metric("Recommendation", decision)
    m5.metric("Risk Segment", grade_group)

    st.markdown(
        f"""
        <div class="footnote-box">
            <b>How to read the result:</b><br>
            The system estimates the borrower's probability of repayment difficulty and converts it into a
            credit grade. This borrower is assigned to <b>{credit_grade}</b>, categorized as
            <b>{grade_group}</b>, with a recommended action of <b>{decision}</b>.
            {"<br><br>Observed outcome in test data: <b>" + str(actual_default) + "</b>." if actual_default is not None else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


# Existing Borrower Mode

if mode == "Existing Borrower":
    st.markdown("### Existing Borrower Assessment")
    st.caption("Select a borrower from the existing portfolio and review the system-generated rating.")

    borrower_options = borrower_profile_ui["SK_ID_CURR"].tolist()
    selected_borrower = st.selectbox("Select borrower ID", borrower_options)

    borrower_row_full = data["app_static"][
        data["app_static"]["SK_ID_CURR"] == selected_borrower
    ].copy()

    borrower_profile_row = borrower_profile_ui[
        borrower_profile_ui["SK_ID_CURR"] == selected_borrower
    ].copy()

    if borrower_profile_row.empty:
        st.error("Borrower profile not found.")
        st.stop()

    borrower_profile_row = borrower_profile_row.iloc[0]

    static_raw = borrower_row_full.drop(
        columns=[c for c in ["SK_ID_CURR", "TARGET"] if c in borrower_row_full.columns]
    )

    static_processed = preprocess_static_row(static_raw, data)

    seq, mask = build_existing_borrower_sequence(selected_borrower, data)
    embedding, attn = get_tcn_embedding(encoder, seq, mask)

    raw_pd, calibrated_pd = score_borrower(
        static_processed,
        embedding,
        xgb_model,
        platt,
        data["emb_cols_v2"],
    )

    credit_grade = assign_credit_grade_from_summary(calibrated_pd, grade_summary)
    decision = assign_decision_from_grade(credit_grade)
    grade_group = assign_grade_group(credit_grade)

    borrower_rank_row = risk_table[risk_table["SK_ID_CURR"] == selected_borrower]
    actual_default = (
        borrower_rank_row["actual_default"].iloc[0]
        if not borrower_rank_row.empty and "actual_default" in borrower_rank_row.columns
        else None
    )

    render_result_summary(
        raw_pd=raw_pd,
        calibrated_pd=calibrated_pd,
        credit_grade=credit_grade,
        decision=decision,
        grade_group=grade_group,
        actual_default=actual_default,
    )

    render_ecl_metrics(selected_borrower)

    st.markdown("### Borrower Profile")
    render_profile_card(borrower_profile_row)

    render_explanation_block(selected_borrower)

    with st.expander("Technical detail: model attention over repayment history"):
        st.caption(
            "This table is mainly for technical review. Higher attention weight means the model focused more on that monthly history step."
        )
        attn_df = pd.DataFrame(
            {
                "History Step": list(range(1, len(attn) + 1)),
                "Model Attention Weight": attn,
            }
        )
        st.dataframe(attn_df, use_container_width=True, hide_index=True)


# Manual Simulation Mode

else:
    st.markdown("### Manual Borrower Simulation")
    st.caption(
        "Modify a borrower profile using business-friendly inputs and test how the credit rating engine responds."
    )

    app_static = data["app_static"].copy()
    template_id = st.selectbox("Choose a base borrower template", app_static["SK_ID_CURR"].tolist())

    template_row = app_static[app_static["SK_ID_CURR"] == template_id].copy().iloc[[0]]
    edited_row = template_row.copy()

    st.markdown(
        """
        <div class="footnote-box">
            Manual simulation starts from an existing borrower template to preserve hidden model features.
            You can adjust the most important business fields below. The system then recalculates the risk score
            using the edited profile.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("manual_form"):
        st.markdown("#### Financial Information")

        f1, f2 = st.columns(2)

        income = f1.number_input(
            "Monthly / annual income amount",
            min_value=0.0,
            value=float(template_row.iloc[0].get("AMT_INCOME_TOTAL", 0) or 0),
            step=1000.0,
            help="Borrower's declared income amount from the application data.",
        )

        credit_amount = f2.number_input(
            "Requested credit amount",
            min_value=0.0,
            value=float(template_row.iloc[0].get("AMT_CREDIT", 0) or 0),
            step=1000.0,
            help="Total credit amount requested or approved.",
        )

        annuity = f1.number_input(
            "Regular payment / annuity amount",
            min_value=0.0,
            value=float(template_row.iloc[0].get("AMT_ANNUITY", 0) or 0),
            step=100.0,
            help="Regular repayment obligation associated with the loan.",
        )

        goods_price = f2.number_input(
            "Goods price",
            min_value=0.0,
            value=float(template_row.iloc[0].get("AMT_GOODS_PRICE", 0) or 0),
            step=1000.0,
            help="Price of the goods linked to the credit application, if applicable.",
        )

        st.markdown("#### Personal and Employment Profile")

        p1, p2 = st.columns(2)

        current_age = years_from_negative_days(template_row.iloc[0].get("DAYS_BIRTH"))
        if current_age is None:
            current_age = 35.0

        age_years = p1.number_input(
            "Age",
            min_value=18.0,
            max_value=80.0,
            value=float(round(current_age, 1)),
            step=1.0,
            help="Borrower's age in years. The app converts this into the model's original day-based format internally.",
        )

        current_employment = years_from_negative_days(template_row.iloc[0].get("DAYS_EMPLOYED"))
        if current_employment is None or current_employment > 60:
            current_employment = 5.0

        employment_years = p2.number_input(
            "Employment length",
            min_value=0.0,
            max_value=50.0,
            value=float(round(current_employment, 1)),
            step=0.5,
            help="Approximate number of years the borrower has been employed.",
        )

        children = p1.number_input(
            "Number of children",
            min_value=0,
            max_value=10,
            value=int(template_row.iloc[0].get("CNT_CHILDREN", 0) or 0),
            step=1,
        )

        st.markdown("#### Categorical Profile")

        c1, c2 = st.columns(2)

        def safe_options(col, fallback):
            if col in app_static.columns:
                vals = sorted(app_static[col].dropna().astype(str).unique().tolist())
                return vals if vals else fallback
            return fallback

        gender_options = safe_options("CODE_GENDER", ["F", "M"])
        income_type_options = safe_options("NAME_INCOME_TYPE", ["Working", "Commercial associate", "Pensioner"])
        education_options = safe_options("NAME_EDUCATION_TYPE", ["Secondary / secondary special", "Higher education"])
        family_options = safe_options("NAME_FAMILY_STATUS", ["Single / not married", "Married", "Civil marriage"])

        gender = c1.selectbox(
            "Gender",
            options=gender_options,
            index=gender_options.index(str(template_row.iloc[0].get("CODE_GENDER"))) if str(template_row.iloc[0].get("CODE_GENDER")) in gender_options else 0,
        )

        income_type = c2.selectbox(
            "Income type",
            options=income_type_options,
            index=income_type_options.index(str(template_row.iloc[0].get("NAME_INCOME_TYPE"))) if str(template_row.iloc[0].get("NAME_INCOME_TYPE")) in income_type_options else 0,
        )

        education_type = c1.selectbox(
            "Education level",
            options=education_options,
            index=education_options.index(str(template_row.iloc[0].get("NAME_EDUCATION_TYPE"))) if str(template_row.iloc[0].get("NAME_EDUCATION_TYPE")) in education_options else 0,
        )

        family_status = c2.selectbox(
            "Family status",
            options=family_options,
            index=family_options.index(str(template_row.iloc[0].get("NAME_FAMILY_STATUS"))) if str(template_row.iloc[0].get("NAME_FAMILY_STATUS")) in family_options else 0,
        )

        owns_car = c1.selectbox(
            "Owns a car",
            options=["Yes", "No"],
            index=0 if str(template_row.iloc[0].get("FLAG_OWN_CAR", "N")).upper() == "Y" else 1,
        )

        owns_realty = c2.selectbox(
            "Owns real estate",
            options=["Yes", "No"],
            index=0 if str(template_row.iloc[0].get("FLAG_OWN_REALTY", "N")).upper() == "Y" else 1,
        )

        temporal_preset = st.selectbox(
            "Repayment history pattern",
            [
                "Stable payer",
                "Mild deterioration",
                "High delinquency",
                "Recovering borrower",
            ],
            help=(
                "This simplified preset controls the simulated 12-month repayment behavior used by the temporal model."
            ),
        )

        submitted = st.form_submit_button("Score borrower")

    if submitted:
        editable_updates = {
            "AMT_INCOME_TOTAL": income,
            "AMT_CREDIT": credit_amount,
            "AMT_ANNUITY": annuity,
            "AMT_GOODS_PRICE": goods_price,
            "CNT_CHILDREN": children,
            "DAYS_BIRTH": negative_days_from_years(age_years),
            "DAYS_EMPLOYED": negative_days_from_years(employment_years),
            "CODE_GENDER": gender,
            "NAME_INCOME_TYPE": income_type,
            "NAME_EDUCATION_TYPE": education_type,
            "NAME_FAMILY_STATUS": family_status,
            "FLAG_OWN_CAR": yes_no_to_flag(owns_car),
            "FLAG_OWN_REALTY": yes_no_to_flag(owns_realty),
        }

        for col, val in editable_updates.items():
            if col in edited_row.columns:
                edited_row.at[edited_row.index[0], col] = val

        static_raw = edited_row.drop(
            columns=[c for c in ["SK_ID_CURR", "TARGET"] if c in edited_row.columns]
        )

        static_processed = preprocess_static_row(static_raw, data)
        seq, mask = build_temporal_preset(data, temporal_preset)
        embedding, attn = get_tcn_embedding(encoder, seq, mask)

        raw_pd, calibrated_pd = score_borrower(
            static_processed,
            embedding,
            xgb_model,
            platt,
            data["emb_cols_v2"],
        )

        credit_grade = assign_credit_grade_from_summary(calibrated_pd, grade_summary)
        decision = assign_decision_from_grade(credit_grade)
        grade_group = assign_grade_group(credit_grade)

        render_result_summary(
            raw_pd=raw_pd,
            calibrated_pd=calibrated_pd,
            credit_grade=credit_grade,
            decision=decision,
            grade_group=grade_group,
        )

        lgd = {
            "AAA": 0.25,
            "AA": 0.25,
            "A": 0.25,
            "BBB": 0.40,
            "BB": 0.40,
            "B": 0.55,
            "CCC": 0.55,
            "CC": 0.70,
            "D": 0.70,
        }.get(credit_grade, 0.55)

<<<<<<< HEAD
        with st.expander("Show edited borrower inputs"):
            st.dataframe(edited_row, use_container_width=True, hide_index=True)
=======
        ead = credit_amount
        ecl = calibrated_pd * lgd * ead

        st.markdown("### Expected Loss View")
        el1, el2, el3 = st.columns(3)
        el1.metric("Loss Severity Assumption", format_pct(lgd, 1))
        el2.metric("Credit Exposure", format_currency(ead))
        el3.metric("Base Expected Loss", format_currency(ecl))

        with st.expander("Technical detail: edited model input"):
            display_updates = pd.DataFrame(
                [{"Field": k, "Internal Model Value": v} for k, v in editable_updates.items()]
            )
            st.dataframe(display_updates, use_container_width=True, hide_index=True)
>>>>>>> 25e2c74 (Update web streamlit)
