import streamlit as st
import pandas as pd
from services.api_client import APIClient

st.set_page_config(page_title="Claims Management - MediPolicy_IQ", page_icon="📋", layout="wide")

st.title("📋 Claims Adjudication & Management")
st.caption("Submit inpatient, outpatient, and pharmacy claims for dynamic AI adjudication and Coordination of Benefits.")

tab1, tab2 = st.tabs(["➕ Submit New Claim", "📑 Processed Claims Log"])

with tab1:
    st.subheader("New Claim Adjudication Entry")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        patient_id = st.number_input("Patient ID", min_value=1, value=1)
        hospital_id = st.number_input("Hospital ID", min_value=1, value=1)
        claim_type = st.selectbox("Claim Type", ["INPATIENT", "OUTPATIENT", "EMERGENCY", "PHARMACY"])
        diagnosis_code = st.text_input("ICD-10 Diagnosis Code", value="ICD10-J18.9")

    with col_b:
        primary_policy_id = st.number_input("Primary Policy ID", min_value=1, value=1)
        secondary_policy_id = st.number_input("Secondary Policy ID (Optional COB)", min_value=0, value=0)
        secondary_policy_val = secondary_policy_id if secondary_policy_id > 0 else None

    st.subheader("Claim Line Items")
    
    items = [
        {"item_description": "Standard Room Rent (4 days)", "category": "ROOM", "cpt_code": "99291", "billed_amount": 28000.0},
        {"item_description": "ICU Support & Monitoring", "category": "ICU", "cpt_code": "99291", "billed_amount": 35000.0},
        {"item_description": "Laparoscopic Surgical Procedure", "category": "PROCEDURE", "cpt_code": "47562", "billed_amount": 65000.0},
        {"item_description": "Pharmacy & Antibiotics", "category": "PHARMACY", "cpt_code": "36415", "billed_amount": 14500.0},
        {"item_description": "Chest X-Ray & Lab Panels", "category": "LAB", "cpt_code": "71045", "billed_amount": 7500.0},
    ]
    
    items_df = st.data_editor(items, num_rows="dynamic", use_container_width=True)
    
    total_billed = sum(float(x.get("billed_amount", 0)) for x in items_df)
    st.info(f"💰 Total Billed Amount: **${total_billed:,.2f}**")

    if st.button("🚀 Run AI Adjudication & Submit Claim", type="primary"):
        payload = {
            "patient_id": patient_id,
            "hospital_id": hospital_id,
            "primary_policy_id": primary_policy_id,
            "secondary_policy_id": secondary_policy_val,
            "claim_type": claim_type,
            "diagnosis_code": diagnosis_code,
            "total_billed_amount": total_billed,
            "items": items_df
        }

        with st.spinner("Executing dynamic rule engine, COB calculator, and fraud risk model..."):
            result = APIClient.submit_claim(payload)

        if result:
            st.success(f"Claim Processed! Number: **{result['claim_number']}**")
            st.metric("Approved Amount", f"${result['approved_amount']:,.2f}", f"Patient Payable: ${result['patient_payable']:,.2f}")
            st.markdown(f"**Status:** `:blue[{result['status']}]` | **Fraud Risk Score:** `{result['fraud_risk_score']}/100`")
            st.info(f"💡 AI Recommendation: {result['ai_recommendation']}")
            
            with st.expander("🔍 Detailed Adjudication & COB Breakdown"):
                st.json(result.get("decision_explanation", {}))
        else:
            st.error("Failed to connect to backend API. Please ensure FastAPI service is active.")

with tab2:
    st.subheader("All System Claims")
    claims = APIClient.get_claims()
    if claims:
        st.dataframe(pd.DataFrame(claims), use_container_width=True)
    else:
        st.info("No claims found in backend database.")
