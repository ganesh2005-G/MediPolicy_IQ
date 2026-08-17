from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.models.models import Tenant, Patient, Hospital, Policy, Claim, ClaimItem, User
from app.core.security import create_access_token

client = TestClient(app)


def test_cross_tenant_claim_submission_isolation():
    """Verify that claim submissions enforce tenant-level resource ownership checks and lists are isolated."""
    with TestClient(app) as test_client:
        db = SessionLocal()
        try:
            # 1. Setup two isolated tenants
            t1 = db.query(Tenant).filter(Tenant.tenant_id == "claims_t1").first()
            if not t1:
                t1 = Tenant(tenant_id="claims_t1", name="Claims T1 Hosp", tenant_type="HOSPITAL")
                db.add(t1)

            t2 = db.query(Tenant).filter(Tenant.tenant_id == "claims_t2").first()
            if not t2:
                t2 = Tenant(tenant_id="claims_t2", name="Claims T2 Hosp", tenant_type="HOSPITAL")
                db.add(t2)
            db.commit()

            # Create mock user profiles in database
            u1 = db.query(User).filter(User.email == "adm1@test.com").first()
            if not u1:
                u1 = User(email="adm1@test.com", hashed_password="xyz", full_name="Admin 1", role="admin", tenant_id="claims_t1")
                db.add(u1)

            u2 = db.query(User).filter(User.email == "adm2@test.com").first()
            if not u2:
                u2 = User(email="adm2@test.com", hashed_password="xyz", full_name="Admin 2", role="admin", tenant_id="claims_t2")
                db.add(u2)
            db.commit()

            admin_token1 = create_access_token(subject="adm1@test.com", role="admin")
            admin_token2 = create_access_token(subject="adm2@test.com", role="admin")

            headers_t1 = {"Authorization": f"Bearer {admin_token1}", "X-Tenant-ID": "claims_t1"}
            headers_t2 = {"Authorization": f"Bearer {admin_token2}", "X-Tenant-ID": "claims_t2"}

            # 2. Add hospital and patient under tenant 1 if missing
            hosp_t1 = db.query(Hospital).filter(Hospital.hospital_code == "HOSP-T1").first()
            if not hosp_t1:
                hosp_t1 = Hospital(hospital_code="HOSP-T1", name="Hosp T1 Fac", is_cashless_network=True, tenant_id="claims_t1")
                db.add(hosp_t1)
                db.commit()

            pat_t1 = db.query(Patient).filter(Patient.patient_code == "PAT-T1").first()
            if not pat_t1:
                pat_t1 = Patient(patient_code="PAT-T1", full_name="Patient T1", dob="1990-01-01", gender="Male", tenant_id="claims_t1")
                db.add(pat_t1)
                db.commit()

            # Add general policy
            pol = db.query(Policy).filter(Policy.policy_number == "POL-TEST-CLAIMS").first()
            if not pol:
                pol = Policy(policy_number="POL-TEST-CLAIMS", insurer_id=1, sum_insured=500000.0, tenant_id="insurer_001")
                db.add(pol)
                db.commit()

            # 3. Submit valid claim under tenant 1 (should succeed)
            claim_payload = {
                "patient_id": pat_t1.id,
                "hospital_id": hosp_t1.id,
                "primary_policy_id": pol.id,
                "secondary_policy_id": None,
                "claim_type": "INPATIENT",
                "diagnosis_code": "ICD10-J18.9",
                "total_billed_amount": 100000.0,
                "items": [
                    {"item_description": "Standard Room Rent (3 days)", "category": "ROOM", "cpt_code": "99291", "billed_amount": 15000.0}
                ]
            }

            res = test_client.post("/api/v1/claims/", json=claim_payload, headers=headers_t1)
            assert res.status_code == 200
            claim_id_t1 = res.json()["id"]

            # 4. Attempt to submit claim under tenant 2 referencing tenant 1's patient (should fail with 400)
            res = test_client.post("/api/v1/claims/", json=claim_payload, headers=headers_t2)
            assert res.status_code == 400
            assert "Patient ID" in res.json()["detail"]

            # 5. Retrieve claims list for tenant 2 (should be empty)
            res = test_client.get("/api/v1/claims/", headers=headers_t2)
            assert res.status_code == 200
            assert len(res.json()) == 0

            # 6. Retrieve claims list for tenant 1 (should return 1 claim)
            res = test_client.get("/api/v1/claims/", headers=headers_t1)
            assert res.status_code == 200
            assert len(res.json()) == 1
            assert res.json()[0]["id"] == claim_id_t1

        finally:
            db.rollback()
            db.query(ClaimItem).filter(ClaimItem.claim_id.in_(
                db.query(Claim.id).filter(Claim.tenant_id.in_(["claims_t1", "claims_t2"]))
            )).delete(synchronize_session=False)
            db.query(Claim).filter(Claim.tenant_id.in_(["claims_t1", "claims_t2"])).delete(synchronize_session=False)
            db.query(User).filter(User.tenant_id.in_(["claims_t1", "claims_t2"])).delete(synchronize_session=False)
            db.query(Patient).filter(Patient.tenant_id.in_(["claims_t1", "claims_t2"])).delete(synchronize_session=False)
            db.query(Hospital).filter(Hospital.tenant_id.in_(["claims_t1", "claims_t2"])).delete(synchronize_session=False)
            db.query(Policy).filter(Policy.policy_number == "POL-TEST-CLAIMS").delete(synchronize_session=False)
            db.query(Tenant).filter(Tenant.tenant_id.in_(["claims_t1", "claims_t2"])).delete(synchronize_session=False)
            db.commit()
            db.close()
