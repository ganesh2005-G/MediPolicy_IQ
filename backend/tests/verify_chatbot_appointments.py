import requests
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

print("Waiting for chatbot & appointment services to initialize...")
time.sleep(2)

# 1. Check current appointments (should be empty initially)
res = requests.get(f"{BASE_URL}/appointments/")
print("Initial Appointments List status:", res.status_code)
initial_count = len(res.json())
print("Initial count:", initial_count)

# 2. Book appointment via RAG Assistant Chatbot
booking_query = {
    "query": "Please book an appointment with Dr. Sarah Jenkins for tomorrow morning",
    "policy_number": "POL-1001-INDIVIDUAL"
}
res = requests.post(f"{BASE_URL}/rag/query", json=booking_query)
print("Booking Query Response status:", res.status_code)
answer = res.json()["answer"]
print("Assistant Answer received successfully.")
assert "Appointment Booked Successfully" in answer or "APT-" in answer

# 3. Check updated appointments (should have 1 new appointment)
res = requests.get(f"{BASE_URL}/appointments/")
print("Updated Appointments List status:", res.status_code, "Count:", len(res.json()))
assert len(res.json()) == initial_count + 1

# 4. Verify Doctor details are mapped correctly in the booking
latest_booking = res.json()[0]
print("Latest Booking Details:")
print("  Doctor:", latest_booking["doctor_name"])
print("  Specialization:", latest_booking["specialization"])
print("  Code:", latest_booking["appointment_code"])
assert latest_booking["doctor_name"] == "Dr. Sarah Jenkins"
assert latest_booking["specialization"] == "Cardiology"

print("\nSUCCESS: AI Chatbot knowledge base and dynamic appointment booking verified with 0 errors!")
