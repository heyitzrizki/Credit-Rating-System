import pandas as pd
import plotly.express as px
import streamlit as st
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))
from utils import load_data_objects, format_pct, format_pd

st.set_page_config(page_title="Portfolio Monitoring", layout="wide")

data = load_data_objects()

risk_table = data["risk_table"].copy()
grade_summary = data["credit_grade_summary"].copy()
decision_summary = data["decision_grade_summary"].copy()
threshold_policy_summary = data["threshold_policy_summary"].copy()
grade_group_summary = data["grade_group_summary"].copy()
executive_summary = data["executive_summary"].copy()

summary = executive_summary.iloc[0]

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1400px;
        }
        .section-note {
            color: #B9C0CB;
            font-size: 0.97rem;
            margin-top: -0.2rem;
            margin-bottom: 1rem;
        }
        .insight-box {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 1rem 1rem 0.75rem 1rem;
            margin-bottom: 0.8rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Portfolio Monitoring")
st.caption("Portfolio quality, risk concentration, and policy comparison across the borrower base")

# KPI ROW
k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Total Borrowers", f"{int(summary['total_borrowers']):,}")
k2.metric("Avg Calibrated PD", format_pd(summary["portfolio_avg_calibrated_pd"], 4))
k3.metric("Observed Default Rate", format_pct(summary["observed_default_rate"], 1))
k4.metric("Investment Grade Share", format_pct(summary["investment_grade_share"], 1))
k5.metric("Review Grade Share", format_pct(summary["review_grade_share"], 1))
k6.metric("High-Risk Share", format_pct(summary["high_risk_exposure"], 1))

st.markdown("")

# PREP DATA
grade_summary = grade_summary.copy()
grade_summary["credit_grade"] = grade_summary["credit_grade"].astype(str)
grade_summary["portfolio_share"] = grade_summary["portfolio_share"] * 100

decision_summary = decision_summary.copy()
decision_summary["decision_recommendation"] = decision_summary["decision_recommendation"].astype(str)
decision_summary["share_of_portfolio"] = decision_summary["share_of_portfolio"] * 100

threshold_policy_summary = threshold_policy_summary.copy()
threshold_policy_summary["decision_pd_threshold"] = threshold_policy_summary["decision_pd_threshold"].astype(str)
threshold_policy_summary["share_of_portfolio"] = threshold_policy_summary["share_of_portfolio"] * 100

grade_group_summary = grade_group_summary.copy()
grade_group_summary["grade_group"] = grade_group_summary["grade_group"].astype(str)
grade_group_summary["share_of_portfolio"] = grade_group_summary["share_of_portfolio"] * 100

# MAIN DISTRIBUTION CHARTS
c1, c2 = st.columns(2)

with c1:
    st.markdown("### Portfolio Distribution by Credit Grade")
    st.markdown(
        '<div class="section-note">Borrower count and portfolio concentration across the AAA–D grade framework.</div>',
        unsafe_allow_html=True,
    )

    fig_grade_dist = px.bar(
        grade_summary,
        x="credit_grade",
        y="borrower_count",
        text="portfolio_share",
    )
    fig_grade_dist.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
    )
    fig_grade_dist.update_layout(
        xaxis_title="Credit Grade",
        yaxis_title="Borrower Count",
        showlegend=False,
        height=420,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_grade_dist, use_container_width=True)

with c2:
    st.markdown("### Portfolio Distribution by Grade Group")
    st.markdown(
        '<div class="section-note">Business grouping of the portfolio into investment grade, review grade, and high-risk segments.</div>',
        unsafe_allow_html=True,
    )

    fig_group_dist = px.pie(
        grade_group_summary,
        names="grade_group",
        values="borrower_count",
        hole=0.55,
    )
    fig_group_dist.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=20, b=20),
        legend_title_text="Grade Group",
    )
    st.plotly_chart(fig_group_dist, use_container_width=True)

# RISK QUALITY CHARTS
r1, r2 = st.columns(2)

with r1:
    st.markdown("### Observed Default Rate by Credit Grade")
    st.markdown(
        '<div class="section-note">Observed default behavior across the rating structure.</div>',
        unsafe_allow_html=True,
    )

    fig_default = px.bar(
        grade_summary,
        x="credit_grade",
        y="observed_default_rate",
        text="observed_default_rate",
    )
    fig_default.update_traces(
        texttemplate="%{text:.2%}",
        textposition="outside",
    )
    fig_default.update_layout(
        xaxis_title="Credit Grade",
        yaxis_title="Observed Default Rate",
        showlegend=False,
        height=380,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_default, use_container_width=True)

with r2:
    st.markdown("### Average Predicted PD by Credit Grade")
    st.markdown(
        '<div class="section-note">Average calibrated default probability inside each rating bucket.</div>',
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

# POLICY COMPARISON
st.markdown("### Policy Comparison")
st.markdown(
    '<div class="section-note">Compare portfolio decision mix under the grade-based policy versus the threshold-based policy reference.</div>',
    unsafe_allow_html=True,
)

grade_policy_compare = decision_summary[["decision_recommendation", "borrower_count", "share_of_portfolio"]].copy()
grade_policy_compare["policy_type"] = "Grade-Based"
grade_policy_compare = grade_policy_compare.rename(columns={"decision_recommendation": "decision"})

threshold_policy_compare = threshold_policy_summary[["decision_pd_threshold", "borrower_count", "share_of_portfolio"]].copy()
threshold_policy_compare["policy_type"] = "Threshold-Based"
threshold_policy_compare = threshold_policy_compare.rename(columns={"decision_pd_threshold": "decision"})

policy_compare = pd.concat([grade_policy_compare, threshold_policy_compare], ignore_index=True)

pc1, pc2 = st.columns((1.1, 1))

with pc1:
    fig_policy = px.bar(
        policy_compare,
        x="decision",
        y="share_of_portfolio",
        color="policy_type",
        barmode="group",
        text="share_of_portfolio",
    )
    fig_policy.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
    )
    fig_policy.update_layout(
        xaxis_title="Decision",
        yaxis_title="Portfolio Share (%)",
        height=420,
        margin=dict(l=20, r=20, t=20, b=20),
        legend_title_text="Policy Type",
    )
    st.plotly_chart(fig_policy, use_container_width=True)

with pc2:
    compare_table = policy_compare.copy()
    compare_table["share_of_portfolio"] = compare_table["share_of_portfolio"].map(lambda x: f"{x:.1f}%")
    compare_table["borrower_count"] = compare_table["borrower_count"].map(lambda x: f"{int(x):,}")
    st.dataframe(
        compare_table[["policy_type", "decision", "borrower_count", "share_of_portfolio"]],
        use_container_width=True,
        hide_index=True,
    )

# PORTFOLIO TABLE
st.markdown("### Portfolio Summary Table")

display_df = grade_summary[
    ["credit_grade", "borrower_count", "portfolio_share", "avg_predicted_pd", "observed_default_rate"]
].copy()

display_df["borrower_count"] = display_df["borrower_count"].map(lambda x: f"{int(x):,}")
display_df["portfolio_share"] = display_df["portfolio_share"].map(lambda x: f"{x:.1f}%")
display_df["avg_predicted_pd"] = display_df["avg_predicted_pd"].map(lambda x: f"{x:.4f}")
display_df["observed_default_rate"] = display_df["observed_default_rate"].map(lambda x: f"{x:.2%}")

st.dataframe(display_df, use_container_width=True, hide_index=True)

# MONITORING INSIGHTS
st.markdown("### Monitoring Highlights")

largest_bucket = grade_summary.sort_values("borrower_count", ascending=False).iloc[0]
highest_default = grade_summary.sort_values("observed_default_rate", ascending=False).iloc[0]
highest_avg_pd = grade_summary.sort_values("avg_predicted_pd", ascending=False).iloc[0]

i1, i2, i3 = st.columns(3)

with i1:
    st.markdown(
        f"""
        <div class="insight-box">
            <b>Largest portfolio concentration</b><br><br>
            The largest concentration is currently in grade <b>{largest_bucket['credit_grade']}</b>,
            representing <b>{largest_bucket['portfolio_share']:.1f}%</b> of the portfolio.
        </div>
        """,
        unsafe_allow_html=True,
    )

with i2:
    st.markdown(
        f"""
        <div class="insight-box">
            <b>Highest observed default pressure</b><br><br>
            Grade <b>{highest_default['credit_grade']}</b> shows the highest observed default rate
            at <b>{highest_default['observed_default_rate']:.2%}</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

with i3:
    st.markdown(
        f"""
        <div class="insight-box">
            <b>Highest average predicted risk</b><br><br>
            Grade <b>{highest_avg_pd['credit_grade']}</b> has the highest average calibrated PD
            at <b>{highest_avg_pd['avg_predicted_pd']:.4f}</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )
