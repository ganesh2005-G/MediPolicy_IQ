import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app


from app.core.security import create_access_token

def test_full_e2e_flow():
    with TestClient(app) as client:
        # 1. Health check
        res = client.get("/")
        assert res.status_code == 200

        # Generate token and default headers
        admin_token = create_access_token(subject="admin@medipolicy.iq", role="admin")
        headers = {"Authorization": f"Bearer {admin_token}", "X-Tenant-ID": "hospital_001"}
        headers_insurer = {"Authorization": f"Bearer {admin_token}", "X-Tenant-ID": "insurer_001"}

        # 2. Patients API
        res = client.get("/api/v1/patients/", headers=headers)
        assert res.status_code == 200
        patients = res.json()
        assert len(patients) > 0, "Database seeding should populate patients on startup"

        # 3. Policies API
        res = client.get("/api/v1/policies/", headers=headers_insurer)

        assert res.status_code == 200
        policies = res.json()
        assert len(policies) > 0, "Database seeding should populate policies on startup"


        # 4. Submit & Adjudicate Claim
        claim_payload = {
            "patient_id": patients[0]["id"],
            "hospital_id": 1,
            "primary_policy_id": policies[0]["id"],
            "secondary_policy_id": None,
            "claim_type": "INPATIENT",
            "diagnosis_code": "ICD10-J18.9",
            "total_billed_amount": 150000.0,
            "items": [
                {"item_description": "Standard Room Rent (4 days)", "category": "ROOM", "cpt_code": "99291", "billed_amount": 28000.0},
                {"item_description": "Laparoscopic Surgery", "category": "PROCEDURE", "cpt_code": "47562", "billed_amount": 65000.0}
            ]
        }
        res = client.post("/api/v1/claims/", json=claim_payload, headers=headers)
        assert res.status_code == 200
        claim_data = res.json()
        assert "claim_number" in claim_data
        assert claim_data["status"] in ["APPROVED", "PARTIALLY_APPROVED", "UNDER_REVIEW", "FLAGGED_FRAUD"]

        # 5. List Claims
        res = client.get("/api/v1/claims/", headers=headers)
        assert res.status_code == 200
        claims = res.json()
        assert len(claims) >= 1

        # 6. Process OCR Document
        res = client.post("/api/v1/ocr/process", data={"doc_type": "INVOICE", "sample_type": "inpatient_bill"}, headers=headers)
        assert res.status_code == 200
        ocr_data = res.json()
        assert "document_code" in ocr_data

        # 7. RAG AI Query
        res = client.post("/api/v1/rag/query", json={"query": "What is the room rent cap?"}, headers=headers)
        assert res.status_code == 200
        rag_data = res.json()
        assert "answer" in rag_data

        # 8. Dashboard Analytics
        res = client.get("/api/v1/analytics/dashboard", headers=headers)
        assert res.status_code == 200
        analytics = res.json()
        assert analytics["total_claims"] >= 1

        print("SUCCESS: All MediPolicy_IQ E2E API routes verified with 0 errors!")



if __name__ == "__main__":
    test_full_e2e_flow()
