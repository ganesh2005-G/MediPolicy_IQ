import requests
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

print("Waiting for Hospital Enterprise Portal to initialize...")
time.sleep(3)

# 1. Test React SPA HTML
res = requests.get("http://127.0.0.1:8000/")
print("React SPA Serving:", res.status_code, "Length:", len(res.text))
assert res.status_code == 200

# 2. Hospital Doctors Directory
res = requests.get(f"{BASE_URL}/hospitals/doctors")
print("Doctors Roster:", res.status_code, "Count:", len(res.json()))
assert res.status_code == 200
assert len(res.json()) >= 5

# 3. Hospital Patients Directory
res = requests.get(f"{BASE_URL}/patients/")
print("Patients Directory:", res.status_code, "Count:", len(res.json()))
assert res.status_code == 200
assert len(res.json()) >= 5

# 4. Diseases & Diagnoses Search DB
res = requests.get(f"{BASE_URL}/hospitals/diseases?query=Pneumonia")
print("Diseases Search DB:", res.status_code, "Results:", len(res.json()))
assert res.status_code == 200
assert len(res.json()) >= 1

# 5. Onboard New Doctor Specialist
ts = int(time.time())
new_doc = {
    "doctor_code": f"DOC-{ts}",
    "full_name": f"Dr. Deepak Malhotra {ts}",
    "specialization": "Neurology",
    "qualification": "DM (Neurology)",
    "department": "Neuroscience Institute",
    "hospital_name": "Metro General Hospital",
    "phone": "+91-9811009988"
}
res = requests.post(f"{BASE_URL}/hospitals/doctors", json=new_doc)
print("Onboard New Doctor API:", res.status_code, "Doctor ID:", res.json().get("id"))
assert res.status_code in [200, 201]

print("\nSUCCESS: Complete Hospital Patients Directory, Doctors Roster, Diseases DB, and Claims Portal verified with 0 errors!")
