import streamlit as st

st.set_page_config(
    page_title="Credit Rating System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }
        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }
        .hero-subtitle {
            font-size: 1.15rem;
            color: #A0A7B4;
            margin-bottom: 1.25rem;
        }
        .hero-card {
            background: linear-gradient(135deg, rgba(20,25,40,0.95), rgba(8,12,22,0.98));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            padding: 2rem 2rem 1.5rem 2rem;
            margin-bottom: 1.25rem;
        }
        .nav-note {
            color: #C7CDD8;
            font-size: 1rem;
            line-height: 1.7;
        }
        .mini-pill {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.08);
            font-size: 0.9rem;
            color: #D7DCE5;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">📊 Credit Rating System</div>
        <div class="hero-subtitle">
            Enterprise dashboard for borrower rating, portfolio monitoring, and high-risk watchlist management
        </div>
        <div>
            <span class="mini-pill">AAA–D Credit Grade Framework</span>
            <span class="mini-pill">Platt-Calibrated PD</span>
            <span class="mini-pill">Decision Support System</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Navigation")
st.markdown(
    """
    <div class="nav-note">
        Use the sidebar to navigate across the system:
        <br><br>
        <b>1. Executive Dashboard</b> — portfolio health and business-level summary<br>
        <b>2. About the System</b> — governance, usage, and rating policy<br>
        <b>3. Borrower Rating &amp; Decisioning</b> — individual borrower assessment<br>
        <b>4. Portfolio Monitoring</b> — segment distribution and policy comparison<br>
        <b>5. High-Risk Watchlist</b> — operational review queue
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "This application is designed for decision support. Final credit decisions should remain subject to analyst or policy review."
)