import streamlit as st
import pandas as pd
import plotly.express as px
from services.api_client import APIClient

st.set_page_config(
    page_title="MediPolicy_IQ - Claims Intelligence Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for modern dark/light contrast
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🏥 MediPolicy_IQ</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Enterprise Healthcare Claims Adjudication & Fraud Intelligence</div>', unsafe_allow_html=True)

# Fetch Analytics from Backend
data = APIClient.get_dashboard_analytics()

if not data:
    st.warning("⚡ Backend API not detected at http://127.0.0.1:8000. Running with demonstration state.")
    data = {
        "total_claims": 14,
        "total_billed_amount": 1850000.0,
        "total_approved_amount": 1420000.0,
        "auto_approval_rate": 85.7,
        "fraud_flagged_claims": 1,
        "pending_claims": 2,
        "recent_claims": []
    }

# Top Metric Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Processed Claims", f"{data['total_claims']}", delta="+12% this month")

with col2:
    st.metric("Total Billed vs Approved", f"${data['total_billed_amount']:,.0f}", f"${data['total_approved_amount']:,.0f} approved")

with col3:
    st.metric("Auto-Approval Rate", f"{data['auto_approval_rate']}%", "Target >80%")

with col4:
    st.metric("Fraud Flagged Risk", f"{data['fraud_flagged_claims']}", "Requires Audit", delta_color="inverse")

st.divider()

# Charts Section
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Claim Adjudication Status Distribution")
    status_df = pd.DataFrame({
        "Status": ["APPROVED", "PARTIALLY_APPROVED", "UNDER_REVIEW", "FLAGGED_FRAUD"],
        "Count": [8, 3, 2, 1]
    })
    fig_pie = px.pie(status_df, names="Status", values="Count", color="Status", color_discrete_map={
        "APPROVED": "#10B981",
        "PARTIALLY_APPROVED": "#3B82F6",
        "UNDER_REVIEW": "#F59E0B",
        "FLAGGED_FRAUD": "#EF4444"
    })
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.subheader("📈 Monthly Claim Processing Volume ($)")
    monthly_df = pd.DataFrame({
        "Month": ["May", "Jun", "Jul"],
        "Billed ($)": [450000, 680000, 720000],
        "Approved ($)": [380000, 540000, 500000]
    })
    fig_bar = px.bar(monthly_df, x="Month", y=["Billed ($)", "Approved ($)"], barmode="group",
                     color_discrete_sequence=["#94A3B8", "#1E40AF"])
    st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("📋 Recent Claim Submissions & AI Decisions")
if data.get("recent_claims"):
    claims_df = pd.DataFrame(data["recent_claims"])
    st.dataframe(claims_df[["claim_number", "claim_type", "total_billed_amount", "approved_amount", "status", "fraud_risk_score"]], use_container_width=True)
else:
    st.info("No claims processed yet. Use the sidebar to navigate to Claims Management and submit a sample claim.")
