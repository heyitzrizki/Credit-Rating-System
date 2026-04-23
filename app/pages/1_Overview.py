import plotly.express as px
import pandas as pd
import streamlit as st

from utils import load_data_objects, format_pct, format_pd

st.set_page_config(page_title="Executive Dashboard", layout="wide")

data = load_data_objects()
metadata = data["metadata"]
risk_table = data["risk_table"].copy()
grade_summary = data["credit_grade_summary"].copy()
decision_summary = data["decision_grade_summary"].copy()
executive_summary = data["executive_summary"].copy()
grade_group_summary = data["grade_group_summary"].copy()

summary = executive_summary.iloc[0]

st.markdown(
    """
    <style>
        .metric-card-label {
            font-size: 0.95rem;
            color: #AAB2BF;
            margin-bottom: 0.2rem;
        }
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
st.caption("Business-level summary of portfolio quality, decision mix, and risk concentration")

# KPI ROW
k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Total Borrowers", f"{int(summary['total_borrowers']):,}")
k2.metric("Portfolio Avg PD", format_pd(summary["portfolio_avg_calibrated_pd"], 4))
k3.metric("Approval Rate", format_pct(summary["approval_rate"], 1))
k4.metric("Review Rate", format_pct(summary["review_rate"], 1))
k5.metric("Reject Rate", format_pct(summary["reject_rate"], 1))
k6.metric("High-Risk Exposure", format_pct(summary["high_risk_exposure"], 1))

st.markdown("")

import plotly.express as px
import pandas as pd
import streamlit as st

from utils import load_data_objects, format_pct, format_pd

st.set_page_config(page_title="Executive Dashboard", layout="wide")

data = load_data_objects()
metadata = data["metadata"]
risk_table = data["risk_table"].copy()
grade_summary = data["credit_grade_summary"].copy()
decision_summary = data["decision_grade_summary"].copy()
executive_summary = data["executive_summary"].copy()
grade_group_summary = data["grade_group_summary"].copy()

summary = executive_summary.iloc[0]

st.markdown(
    """
    <style>
        .metric-card-label {
            font-size: 0.95rem;
            color: #AAB2BF;
            margin-bottom: 0.2rem;
        }
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
st.caption("Business-level summary of portfolio quality, decision mix, and risk concentration")

# ----------------------------
# KPI ROW
# ----------------------------
k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Total Borrowers", f"{int(summary['total_borrowers']):,}")
k2.metric("Portfolio Avg PD", format_pd(summary["portfolio_avg_calibrated_pd"], 4))
k3.metric("Approval Rate", format_pct(summary["approval_rate"], 1))
k4.metric("Review Rate", format_pct(summary["review_rate"], 1))
k5.metric("Reject Rate", format_pct(summary["reject_rate"], 1))
k6.metric("High-Risk Exposure", format_pct(summary["high_risk_exposure"], 1))

st.markdown("")

# ----------------------------
# MAIN CHARTS
# ----------------------------
left, right = st.columns((1.15, 1))

grade_summary["portfolio_share"] = grade_summary["portfolio_share"] * 100
grade_summary["credit_grade"] = grade_summary["credit_grade"].astype(str)

decision_summary["share_of_portfolio"] = decision_summary["share_of_portfolio"] * 100

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
    fig_grade.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
    )
    fig_grade.update_layout(
        xaxis_title="Credit Grade",
        yaxis_title="Borrower Count",
        showlegend=False,
        height=420,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_grade, use_container_width=True)

with right:
    st.markdown("### Decision Recommendation Mix")
    st.markdown(
        '<div class="section-note">Portfolio share by recommended decision outcome.</div>',
        unsafe_allow_html=True,
    )

    fig_decision = px.pie(
        decision_summary,
        names="decision_recommendation",
        values="borrower_count",
        hole=0.55,
    )
    fig_decision.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=20, b=20),
        legend_title_text="Decision",
    )
    st.plotly_chart(fig_decision, use_container_width=True)

# ----------------------------
# RISK QUALITY SNAPSHOT
# ----------------------------
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
    fig_avg_pd.update_traces(
        texttemplate="%{text:.4f}",
        textposition="outside",
    )
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
    fig_odr.update_traces(
        texttemplate="%{text:.2%}",
        textposition="outside",
    )
    fig_odr.update_layout(
        xaxis_title="Credit Grade",
        yaxis_title="Observed Default Rate",
        showlegend=False,
        height=380,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_odr, use_container_width=True)

# ----------------------------
# BUSINESS INSIGHTS
# ----------------------------
st.markdown("### Portfolio Highlights")

investment_share = float(summary["investment_grade_share"])
review_share = float(summary["review_grade_share"])
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
            while high-risk grades (B/C/D) represent <b>{high_risk_share:.1%}</b>.
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

# OPTIONAL COMPACT TABLE
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

# GOVERNANCE STRIP
st.markdown("### System Context")
st.markdown(
    f"""
    <div class="governance-strip">
        <b>Model</b>: {metadata.get("final_model_name", "-")} &nbsp;&nbsp;|&nbsp;&nbsp;
        <b>Calibration</b>: {metadata.get("calibration_method", "-")} &nbsp;&nbsp;|&nbsp;&nbsp;
        <b>Framework</b>: AAA–D Credit Grade &nbsp;&nbsp;|&nbsp;&nbsp;
        <b>Usage</b>: Decision Support Only
    </div>
    """,
    unsafe_allow_html=True,
)
# MAIN CHARTS
left, right = st.columns((1.15, 1))

grade_summary["portfolio_share"] = grade_summary["portfolio_share"] * 100
grade_summary["credit_grade"] = grade_summary["credit_grade"].astype(str)

decision_summary["share_of_portfolio"] = decision_summary["share_of_portfolio"] * 100

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
    fig_grade.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
    )
    fig_grade.update_layout(
        xaxis_title="Credit Grade",
        yaxis_title="Borrower Count",
        showlegend=False,
        height=420,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_grade, use_container_width=True)

with right:
    st.markdown("### Decision Recommendation Mix")
    st.markdown(
        '<div class="section-note">Portfolio share by recommended decision outcome.</div>',
        unsafe_allow_html=True,
    )

    fig_decision = px.pie(
        decision_summary,
        names="decision_recommendation",
        values="borrower_count",
        hole=0.55,
    )
    fig_decision.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=20, b=20),
        legend_title_text="Decision",
    )
    st.plotly_chart(fig_decision, use_container_width=True)

# RISK QUALITY SNAPSHOT
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
    fig_avg_pd.update_traces(
        texttemplate="%{text:.4f}",
        textposition="outside",
    )
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
    fig_odr.update_traces(
        texttemplate="%{text:.2%}",
        textposition="outside",
    )
    fig_odr.update_layout(
        xaxis_title="Credit Grade",
        yaxis_title="Observed Default Rate",
        showlegend=False,
        height=380,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_odr, use_container_width=True)

# BUSINESS INSIGHTS
st.markdown("### Portfolio Highlights")

investment_share = float(summary["investment_grade_share"])
review_share = float(summary["review_grade_share"])
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
            while high-risk grades (B/C/D) represent <b>{high_risk_share:.1%}</b>.
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

# OPTIONAL COMPACT TABLE
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

# GOVERNANCE STRIP
st.markdown("### System Context")
st.markdown(
    f"""
    <div class="governance-strip">
        <b>Model</b>: {metadata.get("final_model_name", "-")} &nbsp;&nbsp;|&nbsp;&nbsp;
        <b>Calibration</b>: {metadata.get("calibration_method", "-")} &nbsp;&nbsp;|&nbsp;&nbsp;
        <b>Framework</b>: AAA–D Credit Grade &nbsp;&nbsp;|&nbsp;&nbsp;
        <b>Usage</b>: Decision Support Only
    </div>
    """,
    unsafe_allow_html=True,
)