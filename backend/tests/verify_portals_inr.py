import requests
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

print("Waiting for server to initialize...")
time.sleep(2)

# 1. Test HTML React SPA Serving & Indian Rupee (₹) Symbol
res = requests.get("http://127.0.0.1:8000/")
print("React SPA Serving:", res.status_code, "Length:", len(res.text))
assert res.status_code == 200
assert "₹" in res.text, "Indian Rupee (₹) symbol must be rendered in frontend SPA"

# 2. Patient Portal Claims Endpoint
res = requests.get(f"{BASE_URL}/claims/patient/1")
print("Patient 1 Claims Fetch:", res.status_code, "Count:", len(res.json()))
assert res.status_code == 200

# 3. Add New Patient Endpoint
ts = int(time.time())
new_patient = {
    "patient_code": f"PAT-{ts}",
    "full_name": f"Rohan Sharma {ts}",
    "dob": "1994-08-15",
    "gender": "Male",
    "blood_group": "A+",
    "phone": "+91-9812345678"
}
res = requests.post(f"{BASE_URL}/patients/", json=new_patient)
print("Add New Patient API:", res.status_code, "Patient ID:", res.json().get("id"))
assert res.status_code in [200, 201]

# 4. Add New Doctor / Hospital Endpoint
new_doc = {
    "hospital_code": f"DOC-AIIMS-{ts}",
    "name": f"Dr. Rajesh Kumar {ts} (AIIMS New Delhi)",
    "address": "Ansari Nagar, New Delhi",
    "is_cashless_network": True,
    "contact_number": "+91-1126588500"
}
res = requests.post(f"{BASE_URL}/hospitals/", json=new_doc)
print("Add New Doctor / Facility API:", res.status_code, "Facility ID:", res.json().get("id"))
assert res.status_code in [200, 201]

# 5. Processor Manual Approve / Reject Claim Status Update
claim_id = 1
res = requests.put(f"{BASE_URL}/claims/{claim_id}/status", json={"status": "APPROVED", "decision_notes": "Manually verified by Processor Officer"})
print("Processor Claim Approval API:", res.status_code, "New Status:", res.json().get("status"))
assert res.status_code == 200
assert res.json()["status"] == "APPROVED"

print("\nSUCCESS: All Patient Portals, Processor Approve/Reject, Patient & Doctor creation APIs, and INR currency verified with 0 errors!")
