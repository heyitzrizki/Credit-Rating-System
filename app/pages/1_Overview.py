<<<<<<< HEAD
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

=======
import pandas as pd
import plotly.express as px
>>>>>>> 25e2c74 (Update web streamlit)
import streamlit as st
import pandas as pd
import plotly.express as px

from utils import format_currency, format_pct, format_pd, load_data_objects

st.title("📊 Executive Overview")

data = load_data_objects()
<<<<<<< HEAD

exec_summary = data["executive_summary"].copy()
grade_summary = data["credit_grade_summary"].copy()
decision_summary = data["decision_grade_summary"].copy()

# Safety cast
=======
metadata = data["metadata"]

grade_summary = data["credit_grade_summary"].copy()
decision_summary = data["decision_grade_summary"].copy()
executive_summary = data["executive_summary"].copy()
macro_stress_summary = data.get("macro_stress_summary", pd.DataFrame()).copy()

summary = executive_summary.iloc[0]

st.markdown(
    """
    <style>
        .section-note {
            color: #B9C0CB;
            font-size: 0.98rem;
            margin-top: -0.25rem;
            margin-bottom: 1rem;
        }
        .insight-box {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 1rem 1rem 0.7rem 1rem;
            margin-bottom: 0.75rem;
        }
        .governance-strip {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 1rem 1rem 0.8rem 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Executive Dashboard")
st.caption(
    "Business-level summary of portfolio quality, credit rating distribution, decision mix, and expected loss view"
)

# KPI Row

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Total Borrowers", f"{int(summary['total_borrowers']):,}")
k2.metric("Portfolio Avg PD", format_pd(summary["portfolio_avg_calibrated_pd"], 4))
k3.metric("Approval Rate", format_pct(summary["approval_rate"], 1))
k4.metric("Review Rate", format_pct(summary["review_rate"], 1))
k5.metric("Reject Rate", format_pct(summary["reject_rate"], 1))
k6.metric("High-Risk Exposure", format_pct(summary["high_risk_exposure"], 1))

# ECL Snapshot

if not macro_stress_summary.empty:
    baseline = macro_stress_summary[
        macro_stress_summary["scenario"].astype(str) == "Baseline"
    ]

    severe = macro_stress_summary[
        macro_stress_summary["scenario"].astype(str) == "Severe Downturn"
    ]

    if not baseline.empty and not severe.empty:
        baseline = baseline.iloc[0]
        severe = severe.iloc[0]

        st.markdown("### Expected Loss Snapshot")

        e1, e2, e3, e4 = st.columns(4)

        e1.metric("Baseline ECL", format_currency(baseline["total_ecl"], 0))
        e2.metric("Severe Stress ECL", format_currency(severe["total_ecl"], 0))
        e3.metric("Stress ECL Uplift", format_currency(severe["ecl_uplift"], 0))
        e4.metric("Stress Uplift %", format_pct(severe["ecl_uplift_pct"], 1))

st.markdown("")

# Prep Data

grade_summary = grade_summary.copy()
grade_summary["portfolio_share"] = grade_summary["portfolio_share"] * 100
>>>>>>> 25e2c74 (Update web streamlit)
grade_summary["credit_grade"] = grade_summary["credit_grade"].astype(str)
decision_summary["decision_recommendation"] = decision_summary["decision_recommendation"].astype(str)

<<<<<<< HEAD
summary = exec_summary.iloc[0]

# =========================
# KPI SECTION
# =========================
st.subheader("Key Portfolio Metrics")

k1, k2, k3, k4 = st.columns(4)
=======
decision_summary = decision_summary.copy()
decision_summary["share_of_portfolio"] = decision_summary["share_of_portfolio"] * 100

# Main Charts

left, right = st.columns((1.15, 1))

with left:
    st.markdown("### Credit Grade Distribution")
    st.markdown(
        '<div class="section-note">Distribution of borrowers across the AAA–D rating framework.</div>',
        unsafe_allow_html=True,
    )

    fig_grade = px.bar(
        grade_summary,
        x="credit_grade",
        y="borrower_count",
        text="portfolio_share",
    )
    fig_grade.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_grade.update_layout(
        xaxis_title="Credit Grade",
        yaxis_title="Borrower Count",
        showlegend=False,
        height=420,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_grade, use_container_width=True)
>>>>>>> 25e2c74 (Update web streamlit)

k1.metric("Portfolio Avg PD", format_pd(summary["portfolio_avg_calibrated_pd"]))
k2.metric("High Risk Exposure (B/C/D)", format_pct(summary["high_risk_exposure"]))
k3.metric("Approval Rate", format_pct(summary["approval_rate"]))
k4.metric("Observed Default Rate", format_pct(summary["observed_default_rate"]))

# =========================
# DISTRIBUTION SECTION
# =========================
st.subheader("Portfolio Distribution")

<<<<<<< HEAD
col1, col2 = st.columns(2)

fig_grade = px.bar(
    grade_summary,
    x="credit_grade",
    y="borrower_count",
    title="Borrower Distribution by Credit Grade"
)
col1.plotly_chart(fig_grade, use_container_width=True, key="overview_grade_distribution")

fig_decision = px.pie(
    decision_summary,
    names="decision_recommendation",
    values="borrower_count",
    title="Decision Distribution"
)
col2.plotly_chart(fig_decision, use_container_width=True, key="overview_decision_distribution")

# =========================
# RISK ANALYSIS
# =========================
st.subheader("Risk Analysis")

col3, col4 = st.columns(2)

fig_avg_pd = px.bar(
    grade_summary,
    x="credit_grade",
    y="avg_predicted_pd",
    title="Average Predicted PD by Grade"
)
col3.plotly_chart(fig_avg_pd, use_container_width=True, key="overview_avg_pd")

fig_odr = px.bar(
    grade_summary,
    x="credit_grade",
    y="observed_default_rate",
    title="Observed Default Rate by Grade"
)
col4.plotly_chart(fig_odr, use_container_width=True, key="overview_odr")

# GAP ANALYSIS
st.subheader("Calibration Gap (Observed vs Predicted)")

grade_summary["gap"] = grade_summary["observed_default_rate"] - grade_summary["avg_predicted_pd"]

fig_gap = px.bar(
    grade_summary,
    x="credit_grade",
    y="gap",
    title="Calibration Gap by Grade"
)
st.plotly_chart(fig_gap, use_container_width=True, key="overview_gap")
=======
# Risk Quality Snapshot

left2, right2 = st.columns(2)

with left2:
    st.markdown("### Average Predicted PD by Grade")
    st.markdown(
        '<div class="section-note">Average calibrated probability of default within each credit grade.</div>',
        unsafe_allow_html=True,
    )

    fig_avg_pd = px.bar(
        grade_summary,
        x="credit_grade",
        y="avg_predicted_pd",
        text="avg_predicted_pd",
    )
    fig_avg_pd.update_traces(texttemplate="%{text:.4f}", textposition="outside")
    fig_avg_pd.update_layout(
        xaxis_title="Credit Grade",
        yaxis_title="Average Calibrated PD",
        showlegend=False,
        height=380,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_avg_pd, use_container_width=True)

with right2:
    st.markdown("### Observed Default Rate by Grade")
    st.markdown(
        '<div class="section-note">Observed default behavior across the rating structure.</div>',
        unsafe_allow_html=True,
    )

    fig_odr = px.bar(
        grade_summary,
        x="credit_grade",
        y="observed_default_rate",
        text="observed_default_rate",
    )
    fig_odr.update_traces(texttemplate="%{text:.2%}", textposition="outside")
    fig_odr.update_layout(
        xaxis_title="Credit Grade",
        yaxis_title="Observed Default Rate",
        showlegend=False,
        height=380,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_odr, use_container_width=True)

# Business Insights

st.markdown("### Portfolio Highlights")

investment_share = float(summary["investment_grade_share"])
high_risk_share = float(summary["high_risk_exposure"])
observed_default_rate = float(summary["observed_default_rate"])

top_grade_row = grade_summary.sort_values("borrower_count", ascending=False).iloc[0]
highest_default_row = grade_summary.sort_values("observed_default_rate", ascending=False).iloc[0]

i1, i2, i3 = st.columns(3)

with i1:
    st.markdown(
        f"""
        <div class="insight-box">
            <b>Portfolio composition</b><br><br>
            Investment-grade borrowers account for <b>{investment_share:.1%}</b> of the portfolio,
            while high-risk grades represent <b>{high_risk_share:.1%}</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

with i2:
    st.markdown(
        f"""
        <div class="insight-box">
            <b>Largest rating bucket</b><br><br>
            The largest borrower concentration is currently in grade <b>{top_grade_row['credit_grade']}</b>,
            with <b>{int(top_grade_row['borrower_count']):,}</b> borrowers.
        </div>
        """,
        unsafe_allow_html=True,
    )

with i3:
    st.markdown(
        f"""
        <div class="insight-box">
            <b>Risk concentration</b><br><br>
            The highest observed default rate appears in grade <b>{highest_default_row['credit_grade']}</b>.
            Portfolio-level observed default rate is <b>{observed_default_rate:.2%}</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.expander("View executive summary table"):
    display_cols = [
        "credit_grade",
        "borrower_count",
        "portfolio_share",
        "avg_predicted_pd",
        "observed_default_rate",
    ]
    display_df = grade_summary[display_cols].copy()
    display_df["portfolio_share"] = display_df["portfolio_share"].map(lambda x: f"{x:.1f}%")
    display_df["avg_predicted_pd"] = display_df["avg_predicted_pd"].map(lambda x: f"{x:.4f}")
    display_df["observed_default_rate"] = display_df["observed_default_rate"].map(lambda x: f"{x:.2%}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("### System Context")
st.markdown(
    f"""
    <div class="governance-strip">
        <b>Model</b>: {metadata.get("final_model_name", "-")} &nbsp;&nbsp;|&nbsp;&nbsp;
        <b>Calibration</b>: {metadata.get("calibration_method", "-")} &nbsp;&nbsp;|&nbsp;&nbsp;
        <b>Framework</b>: AAA–D Credit Grade + ECL Simulation &nbsp;&nbsp;|&nbsp;&nbsp;
        <b>Usage</b>: Decision Support Only
    </div>
    """,
    unsafe_allow_html=True,
)
>>>>>>> 25e2c74 (Update web streamlit)
