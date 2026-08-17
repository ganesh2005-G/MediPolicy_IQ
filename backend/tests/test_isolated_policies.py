from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.models.models import Tenant, Insurer, Policy, PolicyRule, User
from app.core.security import create_access_token

client = TestClient(app)


def test_cross_tenant_policy_isolation():
    """Verify that insurers, policies, and policy rule creations enforce strict tenant boundaries."""
    with TestClient(app) as test_client:
        db = SessionLocal()
        try:
            # 1. Onboard two testing tenants
            tenant1 = db.query(Tenant).filter(Tenant.tenant_id == "policy_t1").first()
            if not tenant1:
                tenant1 = Tenant(tenant_id="policy_t1", name="Policy Tenant 1", tenant_type="HOSPITAL")
                db.add(tenant1)

            tenant2 = db.query(Tenant).filter(Tenant.tenant_id == "policy_t2").first()
            if not tenant2:
                tenant2 = Tenant(tenant_id="policy_t2", name="Policy Tenant 2", tenant_type="HOSPITAL")
                db.add(tenant2)
            db.commit()

            admin_token1 = create_access_token(subject="adm1@test.com", role="admin")
            admin_token2 = create_access_token(subject="adm2@test.com", role="admin")

            headers_t1 = {"Authorization": f"Bearer {admin_token1}", "X-Tenant-ID": "policy_t1"}
            headers_t2 = {"Authorization": f"Bearer {admin_token2}", "X-Tenant-ID": "policy_t2"}

            # 2. Add insurer under tenant 1
            insurer_payload = {
                "insurer_code": "INS_TEST_T1",
                "name": "Insurer T1 Support",
                "contact_email": "t1@insurer.com"
            }
            res = test_client.post("/api/v1/policies/insurers", json=insurer_payload, headers=headers_t1)
            assert res.status_code == 200
            ins_id_t1 = res.json()["id"]

            # 3. Add insurer under tenant 2
            insurer_payload2 = {
                "insurer_code": "INS_TEST_T2",
                "name": "Insurer T2 Support",
                "contact_email": "t2@insurer.com"
            }
            res = test_client.post("/api/v1/policies/insurers", json=insurer_payload2, headers=headers_t2)
            assert res.status_code == 200
            ins_id_t2 = res.json()["id"]

            # 4. Attempt to create policy in tenant 1 linking to insurer in tenant 2 (should fail with 400)
            bad_policy_payload = {
                "policy_number": "POL-BAD-123",
                "insurer_id": ins_id_t2,
                "policy_type": "INDIVIDUAL_HEALTH",
                "sum_insured": 500000.0,
                "deductible": 10000.0,
                "copay_percentage": 10.0,
                "room_rent_cap_per_day": 5000.0,
                "icu_rent_cap_per_day": 10000.0,
                "pre_auth_required": False
            }
            res = test_client.post("/api/v1/policies/", json=bad_policy_payload, headers=headers_t1)
            assert res.status_code == 400
            assert "Linked Insurer not found" in res.json()["detail"]

            # 5. Create policy in tenant 1 with correct insurer (should succeed)
            good_policy_payload = {
                "policy_number": "POL-GOOD-123",
                "insurer_id": ins_id_t1,
                "policy_type": "INDIVIDUAL_HEALTH",
                "sum_insured": 500000.0,
                "deductible": 10000.0,
                "copay_percentage": 10.0,
                "room_rent_cap_per_day": 5000.0,
                "icu_rent_cap_per_day": 10000.0,
                "pre_auth_required": False
            }
            res = test_client.post("/api/v1/policies/", json=good_policy_payload, headers=headers_t1)
            assert res.status_code == 200
            pol_id_t1 = res.json()["id"]

            # 6. Attempt to add a policy rule to tenant 1's policy using tenant 2 credentials (should fail with 404)
            rule_payload = {
                "rule_name": "RULE_CROSS_TENANT",
                "rule_category": "COPAY",
                "expression": "claim_amount > 50000",
                "description": "Cross tenant copay limit rule",
                "action": "DENY",
                "cap_amount": 50000.0,
                "penalty_percentage": 0.0,
                "is_active": True
            }
            res = test_client.post(f"/api/v1/policies/{pol_id_t1}/rules", json=rule_payload, headers=headers_t2)
            assert res.status_code == 404
            assert "Policy not found" in res.json()["detail"]

        finally:
            db.query(PolicyRule).filter(PolicyRule.policy_id.in_(
                db.query(Policy.id).filter(Policy.tenant_id.in_(["policy_t1", "policy_t2"]))
            )).delete(synchronize_session=False)
            db.query(Policy).filter(Policy.tenant_id.in_(["policy_t1", "policy_t2"])).delete(synchronize_session=False)
            db.query(Insurer).filter(Insurer.tenant_id.in_(["policy_t1", "policy_t2"])).delete(synchronize_session=False)
            db.query(Tenant).filter(Tenant.tenant_id.in_(["policy_t1", "policy_t2"])).delete(synchronize_session=False)
            db.commit()
            db.close()
