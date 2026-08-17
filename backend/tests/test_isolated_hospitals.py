from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.models.models import Tenant, Doctor, Patient, User
from app.core.security import create_access_token

client = TestClient(app)


def test_cross_tenant_doctor_and_patient_isolation():
    """Verify that hospital, doctor, and patient listings enforce strict tenant boundaries."""
    with TestClient(app) as test_client:
        db = SessionLocal()
        try:
            # 1. Onboard a secondary test tenant 'hospital_002'
            tenant2 = db.query(Tenant).filter(Tenant.tenant_id == "hospital_002").first()
            if not tenant2:
                tenant2 = Tenant(
                    tenant_id="hospital_002",
                    name="AIIMS Specialty Hospital Support",
                    tenant_type="HOSPITAL"
                )
                db.add(tenant2)
                db.commit()

            # Create test admin users for hospital_001 and hospital_002
            u1_token = create_access_token(subject="admin@medipolicy.iq", role="admin")
            u2_token = create_access_token(subject="admin2@medipolicy.iq", role="admin")

            # Link secondary admin in database if missing
            usr2 = db.query(User).filter(User.email == "admin2@medipolicy.iq").first()
            if not usr2:
                usr2 = User(
                    email="admin2@medipolicy.iq",
                    hashed_password="xyz",
                    full_name="Second Admin",
                    role="admin",
                    tenant_id="hospital_002"
                )
                db.add(usr2)
                db.commit()

            # 2. Add doctor under hospital_002
            doc_payload = {
                "doctor_code": "DOC-H2-99",
                "full_name": "Dr. Isolated Surgeon",
                "specialization": "General Surgery",
                "department": "Surgery Center",
                "hospital_name": "AIIMS Specialty Hospital Support"
            }
            headers_t2 = {"Authorization": f"Bearer {u2_token}", "X-Tenant-ID": "hospital_002"}
            response = test_client.post("/api/v1/hospitals/doctors", json=doc_payload, headers=headers_t2)
            assert response.status_code == 200

            # 3. Retrieve doctor list for hospital_001 (should NOT return Dr. Isolated Surgeon)
            headers_t1 = {"Authorization": f"Bearer {u1_token}", "X-Tenant-ID": "hospital_001"}
            response = test_client.get("/api/v1/hospitals/doctors", headers=headers_t1)
            assert response.status_code == 200
            doctor_names = [d["full_name"] for d in response.json()]
            assert "Dr. Isolated Surgeon" not in doctor_names

            # 4. Retrieve doctor list for hospital_002 (should return Dr. Isolated Surgeon)
            response = test_client.get("/api/v1/hospitals/doctors", headers=headers_t2)
            assert response.status_code == 200
            doctor_names = [d["full_name"] for d in response.json()]
            assert "Dr. Isolated Surgeon" in doctor_names

            # 5. Add patient under hospital_002
            patient_payload = {
                "patient_code": "PAT-H2-99",
                "full_name": "Isolated Patient Name",
                "dob": "1990-01-01",
                "gender": "Male"
            }
            response = test_client.post("/api/v1/patients/", json=patient_payload, headers=headers_t2)
            assert response.status_code == 200
            pat_id = response.json()["id"]

            # 6. Attempt to fetch PAT-H2-99 using hospital_001 credentials (should return 404)
            response = test_client.get(f"/api/v1/patients/{pat_id}", headers=headers_t1)
            assert response.status_code == 404

        finally:
            # Clean up secondary tenant entities
            db.query(User).filter(User.tenant_id == "hospital_002").delete()
            db.query(Doctor).filter(Doctor.tenant_id == "hospital_002").delete()
            db.query(Patient).filter(Patient.tenant_id == "hospital_002").delete()
            db.query(Tenant).filter(Tenant.tenant_id == "hospital_002").delete()
            db.commit()
            db.close()
