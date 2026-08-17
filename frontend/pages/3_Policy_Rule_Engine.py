import streamlit as st
import pandas as pd
from services.api_client import APIClient

st.set_page_config(page_title="Dynamic Rule Engine - MediPolicy_IQ", page_icon="⚙️", layout="wide")

st.title("⚙️ Dynamic Policy Rule Engine Configurator")
st.caption("Configure dynamic database-driven policy limits, deductibles, co-pays, and exclusion rules.")

policies = APIClient.get_policies()

if policies:
    st.subheader("Configured Insurance Policies")
    policies_df = pd.DataFrame(policies)
    st.dataframe(policies_df[["id", "policy_number", "policy_type", "sum_insured", "deductible", "copay_percentage", "room_rent_cap_per_day", "pre_auth_required"]], use_container_width=True)

    selected_policy = st.selectbox("Select Policy to view rules", [p["policy_number"] for p in policies])
    
    policy_obj = next((p for p in policies if p["policy_number"] == selected_policy), None)
    if policy_obj:
        st.markdown(f"### Rules configured for policy: `{selected_policy}`")
        if policy_obj.get("rules"):
            st.dataframe(pd.DataFrame(policy_obj["rules"]), use_container_width=True)
        else:
            st.info("No custom rules configured for this policy yet.")

else:
    st.info("Backend API connection needed to fetch live policies. Sample rules shown below:")
    st.dataframe(pd.DataFrame([
        {"rule_name": "NON_NETWORK_PENALTY_15", "category": "NETWORK", "expression": "non_network_hospital", "action": "PENALTY", "penalty": "15%"},
        {"rule_name": "COSMETIC_EXCLUSION", "category": "EXCLUSION", "expression": "cosmetic_procedure", "action": "DENY", "penalty": "N/A"},
        {"rule_name": "ROOM_RENT_CAP_5000", "category": "SUB_LIMIT", "expression": "room_rent_cap", "action": "CAP", "penalty": "N/A"},
    ]))
