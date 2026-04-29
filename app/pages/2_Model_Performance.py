import streamlit as st

from utils import load_data_objects

st.set_page_config(page_title="About the System", layout="wide")

data = load_data_objects()
metadata = data["metadata"]

st.title("About the System")
st.caption("Methodology, business purpose, model governance, and system limitations.")

st.markdown(
    """
    <style>
        .info-card {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
        }
        .muted {
            color: #B7BFCA;
            line-height: 1.65;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("### What this system does")

st.markdown(
    """
    <div class="info-card">
        This dashboard is a credit risk decision-support system. It estimates borrower repayment risk,
        assigns a credit grade, recommends a business action, estimates expected credit loss, and allows
        portfolio-level and borrower-level stress scenario analysis.
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        """
        <div class="info-card">
            <b>Borrower Rating</b><br><br>
            Converts model-estimated default risk into an AAA–D credit grade and business recommendation.
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="info-card">
            <b>Expected Loss View</b><br><br>
            Estimates expected loss using default risk, loss severity assumption, and credit exposure.
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        """
        <div class="info-card">
            <b>Stress Testing</b><br><br>
            Simulates how borrower risk and portfolio loss may change under adverse conditions.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### Core methodology")

st.markdown(
    """
    The system combines static borrower information with repayment-history patterns. A machine learning model
    estimates borrower repayment risk, and the result is adjusted through probability calibration so that
    the model output can be interpreted more consistently as a risk estimate.

    The rating output is then used in a credit decision-support framework:
    - low-risk grades are mapped to approval-oriented recommendations,
    - medium-risk grades are mapped to review-oriented recommendations,
    - high-risk grades are mapped to rejection or manual underwriting.
    """
)

st.markdown("### Expected Credit Loss framework")

st.markdown(
    """
    Expected loss is calculated using:

    `Expected Loss = Estimated Default Risk × Loss Severity Assumption × Credit Exposure`

    In this project:
    - **Estimated Default Risk** comes from the calibrated credit rating model.
    - **Loss Severity Assumption** is assigned by credit grade because the dataset does not contain actual recovery or write-off outcomes.
    - **Credit Exposure** is proxied using the approved credit amount.
    """
)

st.markdown("### Stress testing approach")

st.markdown(
    """
    The system includes two types of stress testing:

    **Portfolio macro scenario testing** estimates how expected loss changes under baseline, monetary tightening,
    mild recession, and severe downturn scenarios.

    **Borrower stress scenario testing** starts from an existing borrower and applies stress assumptions such as
    income decline, higher credit exposure, unstable employment, or worse repayment behavior.

    These stress tests are simulation tools. They are not retrained macroeconomic forecasting models.
    """
)

st.markdown("### Model governance and limitations")

st.warning(
    """
    This dashboard is for decision support only. It should not be used as an automated final credit decision engine.

    Key limitations:
    - The dataset is a historical benchmark dataset, not a live bank production system.
    - Loss severity is assumption-based because actual recovery and write-off data are unavailable.
    - Stress testing uses scenario assumptions rather than estimated causal macroeconomic effects.
    - Borrower-level explanations are model explanations, not causal proof.
    - Final decisions should remain subject to analyst review, business policy, and regulatory governance.
    """
)

with st.expander("Technical metadata"):
    st.json(metadata)