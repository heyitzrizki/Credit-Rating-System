import pandas as pd
import plotly.express as px
import streamlit as st
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))
from utils import load_data_objects, format_pct, format_pd

st.set_page_config(page_title="High-Risk Watchlist", layout="wide")

data = load_data_objects()
risk_table = data["risk_table"].copy()
top_high_risk = data["top_high_risk"].copy()

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
        .action-box {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 1rem 1rem 0.75rem 1rem;
            margin-bottom: 0.8rem;
        }
        .pill {
            display: inline-block;
            padding: 0.36rem 0.7rem;
            border-radius: 999px;
            margin-right: 0.45rem;
            margin-bottom: 0.4rem;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.08);
            font-size: 0.9rem;
            color: #D9DEE7;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("High-Risk Watchlist")
st.caption("Operational watchlist for high-risk borrowers, priority review, and severity monitoring")

# SAFETY CHECKS
expected_cols = [
    "SK_ID_CURR",
    "pd_calibrated",
    "actual_default",
    "credit_grade",
    "decision_recommendation",
    "portfolio_percentile",
    "risk_priority_flag",
]
missing_cols = [c for c in expected_cols if c not in risk_table.columns]

if missing_cols:
    st.error(
        f"The risk table is missing required columns for the new watchlist view: {missing_cols}. "
        "Please regenerate artifacts from the revised notebook first."
    )
    st.stop()

# FILTERS
st.markdown("### Watchlist Filters")

f1, f2, f3, f4, f5 = st.columns(5)

min_pd = f1.slider("Minimum Calibrated PD", min_value=0.0, max_value=1.0, value=0.10, step=0.01)
top_n = f2.slider("Top N Rows", min_value=10, max_value=300, value=50, step=10)

grade_options = sorted(risk_table["credit_grade"].astype(str).dropna().unique().tolist())
selected_grades = f3.multiselect(
    "Credit Grade",
    options=grade_options,
    default=grade_options,
)

decision_options = sorted(risk_table["decision_recommendation"].astype(str).dropna().unique().tolist())
selected_decisions = f4.multiselect(
    "Decision Recommendation",
    options=decision_options,
    default=decision_options,
)

priority_options = sorted(risk_table["risk_priority_flag"].astype(str).dropna().unique().tolist())
selected_priority = f5.multiselect(
    "Priority Flag",
    options=priority_options,
    default=priority_options,
)

show_defaults_only = st.checkbox("Show only actual defaults in test data", value=False)

# FILTER DATA
filtered = risk_table.copy()
filtered["credit_grade"] = filtered["credit_grade"].astype(str)
filtered["decision_recommendation"] = filtered["decision_recommendation"].astype(str)
filtered["risk_priority_flag"] = filtered["risk_priority_flag"].astype(str)

filtered = filtered[
    (filtered["pd_calibrated"] >= min_pd)
    & (filtered["credit_grade"].isin(selected_grades))
    & (filtered["decision_recommendation"].isin(selected_decisions))
    & (filtered["risk_priority_flag"].isin(selected_priority))
]

if show_defaults_only:
    filtered = filtered[filtered["actual_default"] == 1]

filtered = filtered.sort_values("pd_calibrated", ascending=False).reset_index(drop=True)
filtered_display = filtered.head(top_n).copy()

# KPI ROW
st.markdown("### Watchlist Summary")

if filtered.empty:
    st.warning("No borrowers match the current filter settings.")
    st.stop()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Borrowers in Watchlist", f"{len(filtered):,}")
k2.metric("Avg Calibrated PD", format_pd(filtered["pd_calibrated"].mean(), 4))
k3.metric("Observed Default Rate", format_pct(filtered["actual_default"].mean(), 1))
k4.metric("Portfolio Share", format_pct(len(filtered) / len(risk_table), 1))
k5.metric(
    "High-Risk Grades",
    f"{int(filtered['credit_grade'].isin(['B','C','D']).sum()):,}"
)

# SEVERITY VISUALS
c1, c2 = st.columns(2)

with c1:
    st.markdown("### Watchlist Distribution by Credit Grade")
    st.markdown(
        '<div class="section-note">Risk concentration across rating buckets inside the filtered watchlist.</div>',
        unsafe_allow_html=True,
    )

    grade_dist = (
        filtered.groupby("credit_grade", as_index=False)
        .size()
        .rename(columns={"size": "borrower_count"})
    )

    fig_grade = px.bar(
        grade_dist,
        x="credit_grade",
        y="borrower_count",
        text="borrower_count",
    )
    fig_grade.update_traces(textposition="outside")
    fig_grade.update_layout(
        xaxis_title="Credit Grade",
        yaxis_title="Borrower Count",
        showlegend=False,
        height=380,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_grade, use_container_width=True)

with c2:
    st.markdown("### Calibrated PD Distribution")
    st.markdown(
        '<div class="section-note">Severity distribution of calibrated default probability inside the watchlist.</div>',
        unsafe_allow_html=True,
    )

    fig_hist = px.histogram(
        filtered,
        x="pd_calibrated",
        nbins=20,
    )
    fig_hist.update_layout(
        xaxis_title="Calibrated PD",
        yaxis_title="Borrower Count",
        showlegend=False,
        height=380,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ACTION PANEL
st.markdown("### Operational Priorities")

priority_counts = (
    filtered.groupby("risk_priority_flag", as_index=False)
    .size()
    .rename(columns={"size": "borrower_count"})
    .sort_values("borrower_count", ascending=False)
)

a1, a2, a3 = st.columns(3)

immediate_count = int((filtered["risk_priority_flag"] == "Immediate Review").sum())
manual_count = int((filtered["risk_priority_flag"] == "Manual Underwriting").sum())
analyst_count = int((filtered["risk_priority_flag"] == "Analyst Review").sum())

with a1:
    st.markdown(
        f"""
        <div class="action-box">
            <b>Immediate Review</b><br><br>
            <span class="pill">Count: {immediate_count:,}</span><br>
            Borrowers flagged in the most severe segment should be prioritized for urgent review.
        </div>
        """,
        unsafe_allow_html=True,
    )

with a2:
    st.markdown(
        f"""
        <div class="action-box">
            <b>Manual Underwriting</b><br><br>
            <span class="pill">Count: {manual_count:,}</span><br>
            Borderline but elevated-risk borrowers may require manual underwriting and tighter verification.
        </div>
        """,
        unsafe_allow_html=True,
    )

with a3:
    st.markdown(
        f"""
        <div class="action-box">
            <b>Analyst Review</b><br><br>
            <span class="pill">Count: {analyst_count:,}</span><br>
            Review-grade borrowers can be monitored or escalated based on supporting documentation.
        </div>
        """,
        unsafe_allow_html=True,
    )

# WATCHLIST TABLE
st.markdown("### Watchlist Table")
st.markdown(
    '<div class="section-note">Filtered borrower list sorted by highest calibrated PD.</div>',
    unsafe_allow_html=True,
)

table_cols = [
    "SK_ID_CURR",
    "pd_calibrated",
    "credit_grade",
    "decision_recommendation",
    "risk_priority_flag",
    "portfolio_percentile",
    "actual_default",
]

available_cols = [c for c in table_cols if c in filtered_display.columns]
watchlist_table = filtered_display[available_cols].copy()

if "pd_calibrated" in watchlist_table.columns:
    watchlist_table["pd_calibrated"] = watchlist_table["pd_calibrated"].map(lambda x: f"{x:.4f}")
if "portfolio_percentile" in watchlist_table.columns:
    watchlist_table["portfolio_percentile"] = watchlist_table["portfolio_percentile"].map(lambda x: f"{x:.1%}")
if "actual_default" in watchlist_table.columns:
    watchlist_table["actual_default"] = watchlist_table["actual_default"].map(lambda x: int(x))

st.dataframe(watchlist_table, use_container_width=True, hide_index=True)

# TOP HIGH-RISK REFERENCE
with st.expander("Show original top high-risk reference table"):
    ref_df = top_high_risk.copy()

    for col in ["pd_calibrated", "portfolio_percentile"]:
        if col in ref_df.columns:
            if col == "pd_calibrated":
                ref_df[col] = ref_df[col].map(lambda x: f"{x:.4f}")
            else:
                ref_df[col] = ref_df[col].map(lambda x: f"{x:.1%}")

    st.dataframe(ref_df, use_container_width=True, hide_index=True)
