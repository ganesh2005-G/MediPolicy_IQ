from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.models.models import Tenant, TenantConfiguration, Appointment, User
from app.core.security import create_access_token

client = TestClient(app)


def test_cross_tenant_rag_assistant_isolation():
    """Verify that RAG assistant replies and appointment bookings respect TenantConfiguration templates."""
    with TestClient(app) as test_client:
        db = SessionLocal()
        try:
            # 1. Setup two isolated tenants with distinct configs
            t1 = db.query(Tenant).filter(Tenant.tenant_id == "rag_t1").first()
            if not t1:
                t1 = Tenant(tenant_id="rag_t1", name="RAG T1 Hosp", tenant_type="HOSPITAL")
                db.add(t1)

            t2 = db.query(Tenant).filter(Tenant.tenant_id == "rag_t2").first()
            if not t2:
                t2 = Tenant(tenant_id="rag_t2", name="RAG T2 Hosp", tenant_type="HOSPITAL")
                db.add(t2)
            db.commit()

            c1 = db.query(TenantConfiguration).filter(TenantConfiguration.tenant_id == "rag_t1").first()
            if not c1:
                c1 = TenantConfiguration(
                    tenant_id="rag_t1",
                    features={"claims": True, "ocr": True, "ai_assistant": True},
                    ai_config={"assistant_name": "T1-HealthBot", "tone": "concise", "instructions": "Consultations helper."}
                )
                db.add(c1)

            c2 = db.query(TenantConfiguration).filter(TenantConfiguration.tenant_id == "rag_t2").first()
            if not c2:
                c2 = TenantConfiguration(
                    tenant_id="rag_t2",
                    features={"claims": True, "ocr": True, "ai_assistant": True},
                    ai_config={"assistant_name": "T2-Navigator", "tone": "warm", "instructions": "Care router guide."}
                )
                db.add(c2)
            db.commit()

            # Create mock user profiles in database
            u1 = db.query(User).filter(User.email == "rag_adm1@test.com").first()
            if not u1:
                u1 = User(email="rag_adm1@test.com", hashed_password="xyz", full_name="Admin 1", role="admin", tenant_id="rag_t1")
                db.add(u1)

            u2 = db.query(User).filter(User.email == "rag_adm2@test.com").first()
            if not u2:
                u2 = User(email="rag_adm2@test.com", hashed_password="xyz", full_name="Admin 2", role="admin", tenant_id="rag_t2")
                db.add(u2)
            db.commit()

            admin_token1 = create_access_token(subject="rag_adm1@test.com", role="admin")
            admin_token2 = create_access_token(subject="rag_adm2@test.com", role="admin")

            headers_t1 = {"Authorization": f"Bearer {admin_token1}", "X-Tenant-ID": "rag_t1"}
            headers_t2 = {"Authorization": f"Bearer {admin_token2}", "X-Tenant-ID": "rag_t2"}

            # 2. Query RAG under tenant 1 (should return T1-HealthBot branding)
            payload = {"query": "Tell me about room rent limits"}
            res = test_client.post("/api/v1/rag/query", json=payload, headers=headers_t1)
            assert res.status_code == 200
            assert "T1-HealthBot" in res.json()["answer"]

            # 3. Query RAG under tenant 2 (should return T2-Navigator branding)
            res = test_client.post("/api/v1/rag/query", json=payload, headers=headers_t2)
            assert res.status_code == 200
            assert "T2-Navigator" in res.json()["answer"]

            # 4. Trigger booking intent under tenant 1
            booking_payload = {"query": "Book morning cardiology appointment with Dr. Sarah Jenkins"}
            res = test_client.post("/api/v1/rag/query", json=booking_payload, headers=headers_t1)
            assert res.status_code == 200
            assert "Booked Successfully" in res.json()["answer"]
            assert "T1-HealthBot" in res.json()["answer"]

            # 5. Verify the created appointment belongs strictly to rag_t1
            appts_t1 = db.query(Appointment).filter(Appointment.tenant_id == "rag_t1").all()
            assert len(appts_t1) == 1
            assert appts_t1[0].doctor_name == "Dr. Sarah Jenkins"

            # Check that rag_t2 appointments remain empty
            appts_t2 = db.query(Appointment).filter(Appointment.tenant_id == "rag_t2").all()
            assert len(appts_t2) == 0

        finally:
            db.rollback()
            db.query(Appointment).filter(Appointment.tenant_id.in_(["rag_t1", "rag_t2"])).delete(synchronize_session=False)
            db.query(User).filter(User.tenant_id.in_(["rag_t1", "rag_t2"])).delete(synchronize_session=False)
            db.query(TenantConfiguration).filter(TenantConfiguration.tenant_id.in_(["rag_t1", "rag_t2"])).delete(synchronize_session=False)
            db.query(Tenant).filter(Tenant.tenant_id.in_(["rag_t1", "rag_t2"])).delete(synchronize_session=False)
            db.commit()
            db.close()
