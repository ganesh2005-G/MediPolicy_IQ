import requests
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

print("Waiting for server to warm up...")
time.sleep(3)

# 1. Test React Frontend App Root HTML
res = requests.get("http://127.0.0.1:8000/")
print("React SPA Root HTML:", res.status_code, "Length:", len(res.text))
assert res.status_code == 200
assert "<div id=\"root\"></div>" in res.text

# 2. Test Multi-Role Logins
roles_to_test = [
    ("Admin Login", "admin@medipolicy.iq", "Admin123!", "admin"),
    ("Doctor Login", "doctor@medipolicy.iq", "Doctor123!", "doctor"),
    ("Processor Login", "processor@medipolicy.iq", "Processor123!", "claim_processor"),
    ("Patient Login", "patient@medipolicy.iq", "Patient123!", "patient"),
]

for label, email, password, expected_role in roles_to_test:
    res = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    print(f"[{label}] Status:", res.status_code, "Token received:", "access_token" in res.json())
    assert res.status_code == 200
    token = res.json()["access_token"]

    # Test /auth/me profile check with JWT Token
    profile_res = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {token}"})
    print(f"[{label}] Profile Check:", profile_res.status_code, "User Role:", profile_res.json().get("role"))
    assert profile_res.status_code == 200
    assert profile_res.json()["role"] == expected_role

print("\nSUCCESS: All Multi-Role Logins (Admin, Doctor, Processor, Patient) & React SPA served with 0 errors!")
