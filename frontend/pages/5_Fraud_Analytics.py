import streamlit as st
import pandas as pd
import plotly.express as px
from services.api_client import APIClient

st.set_page_config(page_title="Fraud Risk & Audit - MediPolicy_IQ", page_icon="🛡️", layout="wide")

st.title("🛡️ Claim Fraud Detection & Risk Analytics")
st.caption("Explainable AI risk scoring, anomaly detection, and audit trail for claims processors.")

st.subheader("System Fraud Risk Overview")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Flagged Claims", "1", "Requires Investigation", delta_color="inverse")
with col2:
    st.metric("Average System Risk Score", "14.2 / 100", "-2.1 vs last week")
with col3:
    st.metric("Detection Rules Active", "12 Dynamic Rules", "100% Operational")

st.divider()

st.subheader("📊 Fraud Risk Score Distribution")

mock_risk_data = pd.DataFrame([
    {"Claim Number": "CLM-A89102", "Risk Score": 85.0, "Risk Level": "HIGH", "Primary Flag": "HIGH_VALUE_CLAIM (>500k)", "Status": "FLAGGED_FRAUD"},
    {"Claim Number": "CLM-B77211", "Risk Score": 42.5, "Risk Level": "MEDIUM", "Primary Flag": "EXCESSIVE_LENGTH_OF_STAY", "Status": "UNDER_REVIEW"},
    {"Claim Number": "CLM-C10992", "Risk Score": 12.0, "Risk Level": "LOW", "Primary Flag": "None", "Status": "APPROVED"},
    {"Claim Number": "CLM-D44105", "Risk Score": 8.0, "Risk Level": "LOW", "Primary Flag": "None", "Status": "APPROVED"},
])

fig = px.histogram(mock_risk_data, x="Risk Score", color="Risk Level",
                   color_discrete_map={"HIGH": "#EF4444", "MEDIUM": "#F59E0B", "LOW": "#10B981"},
                   nbins=10, title="Risk Score Distribution Across Active Claims")
st.plotly_chart(fig, use_container_width=True)

st.subheader("🚨 Flagged Claims & Risk Breakdown")
st.dataframe(mock_risk_data, use_container_width=True)
