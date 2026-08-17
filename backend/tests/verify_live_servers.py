import requests
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"
FRONTEND_URL = "http://127.0.0.1:8501"

print("Waiting for servers to warm up...")
time.sleep(3)

# 1. Health Check
res = requests.get("http://127.0.0.1:8000/")
print("Backend Root Health:", res.status_code, res.json())
assert res.status_code == 200

# 2. Patients API
res = requests.get(f"{BASE_URL}/patients/")
print("Patients API:", res.status_code, f"{len(res.json())} patients found")
assert res.status_code == 200

# 3. Policies API
res = requests.get(f"{BASE_URL}/policies/")
print("Policies API:", res.status_code, f"{len(res.json())} policies found")
assert res.status_code == 200

# 4. Submit Claim API
claim_payload = {
    "patient_id": 1,
    "hospital_id": 1,
    "primary_policy_id": 1,
    "secondary_policy_id": None,
    "claim_type": "INPATIENT",
    "diagnosis_code": "ICD10-J18.9",
    "total_billed_amount": 150000.0,
    "items": [
        {"item_description": "Standard Room Rent (4 days)", "category": "ROOM", "cpt_code": "99291", "billed_amount": 28000.0},
        {"item_description": "Laparoscopic Surgical Procedure", "category": "PROCEDURE", "cpt_code": "47562", "billed_amount": 65000.0}
    ]
}
res = requests.post(f"{BASE_URL}/claims/", json=claim_payload)
print("Submit Claim API:", res.status_code, "Claim Number:", res.json().get("claim_number"), "Status:", res.json().get("status"))
assert res.status_code == 200

# 5. Process Document OCR API
res = requests.post(f"{BASE_URL}/ocr/process", data={"doc_type": "INVOICE", "sample_type": "inpatient_bill"})
print("Document OCR API:", res.status_code, "Doc Code:", res.json().get("document_code"))
assert res.status_code == 200

# 6. Policy RAG Assistant API
res = requests.post(f"{BASE_URL}/rag/query", json={"query": "What is the daily room rent cap?"})
print("RAG AI Query API:", res.status_code, "Answer:", res.json().get("answer"))
assert res.status_code == 200

# 7. Dashboard Analytics API
res = requests.get(f"{BASE_URL}/analytics/dashboard")
print("Analytics Dashboard API:", res.status_code, f"{res.json().get('total_claims')} total claims recorded")
assert res.status_code == 200

# 8. Check Streamlit Frontend HTML response
res = requests.get(FRONTEND_URL)
print("Streamlit Frontend HTTP:", res.status_code)
assert res.status_code == 200

print("\nSUCCESS: All live backend & frontend services tested and verified with 0 errors!")
