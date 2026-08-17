from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.models.models import Tenant, Document, User
from app.core.security import create_access_token

client = TestClient(app)


def test_cross_tenant_ocr_document_isolation():
    """Verify that uploaded and processed documents are strictly tenant isolated."""
    with TestClient(app) as test_client:
        db = SessionLocal()
        try:
            # 1. Setup two isolated tenants
            t1 = db.query(Tenant).filter(Tenant.tenant_id == "ocr_t1").first()
            if not t1:
                t1 = Tenant(tenant_id="ocr_t1", name="OCR T1 Hosp", tenant_type="HOSPITAL")
                db.add(t1)

            t2 = db.query(Tenant).filter(Tenant.tenant_id == "ocr_t2").first()
            if not t2:
                t2 = Tenant(tenant_id="ocr_t2", name="OCR T2 Hosp", tenant_type="HOSPITAL")
                db.add(t2)
            db.commit()

            # Create mock user profiles in database
            u1 = db.query(User).filter(User.email == "ocr_adm1@test.com").first()
            if not u1:
                u1 = User(email="ocr_adm1@test.com", hashed_password="xyz", full_name="Admin 1", role="admin", tenant_id="ocr_t1")
                db.add(u1)

            u2 = db.query(User).filter(User.email == "ocr_adm2@test.com").first()
            if not u2:
                u2 = User(email="ocr_adm2@test.com", hashed_password="xyz", full_name="Admin 2", role="admin", tenant_id="ocr_t2")
                db.add(u2)
            db.commit()

            admin_token1 = create_access_token(subject="ocr_adm1@test.com", role="admin")
            admin_token2 = create_access_token(subject="ocr_adm2@test.com", role="admin")

            headers_t1 = {"Authorization": f"Bearer {admin_token1}", "X-Tenant-ID": "ocr_t1"}
            headers_t2 = {"Authorization": f"Bearer {admin_token2}", "X-Tenant-ID": "ocr_t2"}

            # 2. Process document under tenant 1
            payload = {"doc_type": "INVOICE", "sample_type": "inpatient_bill"}
            res = test_client.post("/api/v1/ocr/process", data=payload, headers=headers_t1)
            assert res.status_code == 200
            doc_code_t1 = res.json()["document_code"]

            # 3. Retrieve document list for tenant 2 (should be empty)
            res = test_client.get("/api/v1/ocr/", headers=headers_t2)
            assert res.status_code == 200
            assert len(res.json()) == 0

            # 4. Retrieve document list for tenant 1 (should return 1 document)
            res = test_client.get("/api/v1/ocr/", headers=headers_t1)
            assert res.status_code == 200
            assert len(res.json()) == 1
            assert res.json()[0]["document_code"] == doc_code_t1

            # 5. Try to retrieve details of tenant 1's document using tenant 2's headers (should return 404)
            res = test_client.get(f"/api/v1/ocr/{doc_code_t1}", headers=headers_t2)
            assert res.status_code == 404

            # 6. Retrieve details using tenant 1's headers (should succeed)
            res = test_client.get(f"/api/v1/ocr/{doc_code_t1}", headers=headers_t1)
            assert res.status_code == 200

        finally:
            db.rollback()
            db.query(Document).filter(Document.tenant_id.in_(["ocr_t1", "ocr_t2"])).delete(synchronize_session=False)
            db.query(User).filter(User.tenant_id.in_(["ocr_t1", "ocr_t2"])).delete(synchronize_session=False)
            db.query(Tenant).filter(Tenant.tenant_id.in_(["ocr_t1", "ocr_t2"])).delete(synchronize_session=False)
            db.commit()
            db.close()
