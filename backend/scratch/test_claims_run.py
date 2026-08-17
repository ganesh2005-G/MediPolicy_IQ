from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.models.models import Tenant, Patient, Hospital, Policy, User
from app.core.security import create_access_token

client = TestClient(app)

with TestClient(app) as test_client:
    db = SessionLocal()
    # Onboard tenant
    t1 = db.query(Tenant).filter(Tenant.tenant_id == "claims_t1").first()
    if not t1:
        t1 = Tenant(tenant_id="claims_t1", name="Claims T1 Hosp", tenant_type="HOSPITAL")
        db.add(t1)
        db.commit()

    admin_token1 = create_access_token(subject="adm1@test.com", role="admin")
    headers_t1 = {"Authorization": f"Bearer {admin_token1}", "X-Tenant-ID": "claims_t1"}

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

    pol = db.query(Policy).filter(Policy.policy_number == "POL-TEST-CLAIMS").first()
    if not pol:
        pol = Policy(policy_number="POL-TEST-CLAIMS", insurer_id=1, sum_insured=500000.0, tenant_id="insurer_001")
        db.add(pol)
        db.commit()

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
    print("STATUS CODE:", res.status_code)
    print("RESPONSE BODY:", res.text)
