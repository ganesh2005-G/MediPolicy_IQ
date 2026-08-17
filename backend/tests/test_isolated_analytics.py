from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.models.models import Tenant, Claim, AuditLog, User
from app.core.security import create_access_token

client = TestClient(app)


def test_cross_tenant_analytics_and_audit_isolation():
    """Verify that analytics dashboards and system audit logs are isolated by tenant context."""
    with TestClient(app) as test_client:
        db = SessionLocal()
        try:
            # 1. Setup two isolated tenants
            t1 = db.query(Tenant).filter(Tenant.tenant_id == "anal_t1").first()
            if not t1:
                t1 = Tenant(tenant_id="anal_t1", name="Anal T1 Hosp", tenant_type="HOSPITAL")
                db.add(t1)

            t2 = db.query(Tenant).filter(Tenant.tenant_id == "anal_t2").first()
            if not t2:
                t2 = Tenant(tenant_id="anal_t2", name="Anal T2 Hosp", tenant_type="HOSPITAL")
                db.add(t2)
            db.commit()

            # Create mock user profiles in database
            u1 = db.query(User).filter(User.email == "anal_adm1@test.com").first()
            if not u1:
                u1 = User(email="anal_adm1@test.com", hashed_password="xyz", full_name="Admin 1", role="admin", tenant_id="anal_t1")
                db.add(u1)

            u2 = db.query(User).filter(User.email == "anal_adm2@test.com").first()
            if not u2:
                u2 = User(email="anal_adm2@test.com", hashed_password="xyz", full_name="Admin 2", role="admin", tenant_id="anal_t2")
                db.add(u2)
            db.commit()

            admin_token1 = create_access_token(subject="anal_adm1@test.com", role="admin")
            admin_token2 = create_access_token(subject="anal_adm2@test.com", role="admin")

            headers_t1 = {"Authorization": f"Bearer {admin_token1}", "X-Tenant-ID": "anal_t1"}
            headers_t2 = {"Authorization": f"Bearer {admin_token2}", "X-Tenant-ID": "anal_t2"}

            # 2. Add mock claim for tenant 1
            claim1 = Claim(
                claim_number="CLM-ANAL-1",
                patient_id=1,
                hospital_id=1,
                primary_policy_id=1,
                claim_type="INPATIENT",
                total_billed_amount=250000.0,
                approved_amount=200000.0,
                status="APPROVED",
                tenant_id="anal_t1"
            )
            db.add(claim1)

            # 3. Add mock claim for tenant 2
            claim2 = Claim(
                claim_number="CLM-ANAL-2",
                patient_id=1,
                hospital_id=1,
                primary_policy_id=1,
                claim_type="OUTPATIENT",
                total_billed_amount=50000.0,
                approved_amount=40000.0,
                status="APPROVED",
                tenant_id="anal_t2"
            )
            db.add(claim2)
            db.commit()

            # 4. Add mock audit logs for both tenants
            audit1 = AuditLog(tenant_id="anal_t1", action="SUBMIT_CLAIM", entity_type="CLAIM", user_email="anal_adm1@test.com", details="Mock submission")
            audit2 = AuditLog(tenant_id="anal_t2", action="SUBMIT_CLAIM", entity_type="CLAIM", user_email="anal_adm2@test.com", details="Mock submission")
            db.add_all([audit1, audit2])
            db.commit()

            # 5. Fetch Dashboard Analytics for Tenant 1
            res = test_client.get("/api/v1/analytics/dashboard", headers=headers_t1)
            assert res.status_code == 200
            data_t1 = res.json()
            assert data_t1["total_claims"] == 1
            assert data_t1["total_billed_amount"] == 250000.0

            # 6. Fetch Dashboard Analytics for Tenant 2
            res = test_client.get("/api/v1/analytics/dashboard", headers=headers_t2)
            assert res.status_code == 200
            data_t2 = res.json()
            assert data_t2["total_claims"] == 1
            assert data_t2["total_billed_amount"] == 50000.0

            # 7. Fetch Audit Logs list for Tenant 1 (should only contain 1 log)
            res = test_client.get("/api/v1/analytics/audit-logs", headers=headers_t1)
            assert res.status_code == 200
            logs_t1 = res.json()
            assert len(logs_t1) == 1
            assert logs_t1[0]["tenant_id"] == "anal_t1"

            # 8. Fetch Audit Logs list for Tenant 2 (should only contain 1 log)
            res = test_client.get("/api/v1/analytics/audit-logs", headers=headers_t2)
            assert res.status_code == 200
            logs_t2 = res.json()
            assert len(logs_t2) == 1
            assert logs_t2[0]["tenant_id"] == "anal_t2"

        finally:
            db.rollback()
            db.query(Claim).filter(Claim.tenant_id.in_(["anal_t1", "anal_t2"])).delete(synchronize_session=False)
            db.query(AuditLog).filter(AuditLog.tenant_id.in_(["anal_t1", "anal_t2"])).delete(synchronize_session=False)
            db.query(User).filter(User.tenant_id.in_(["anal_t1", "anal_t2"])).delete(synchronize_session=False)
            db.query(Tenant).filter(Tenant.tenant_id.in_(["anal_t1", "anal_t2"])).delete(synchronize_session=False)
            db.commit()
            db.close()
