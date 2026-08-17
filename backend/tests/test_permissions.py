from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.models.models import User, Tenant
from app.core.security import create_access_token
import pytest

client = TestClient(app)


def test_permission_based_access_control():
    """Verify that permission-based RBAC allows authorized roles and blocks unauthorized roles."""
    with TestClient(app) as test_client:
        # Create test users with different roles
        db = SessionLocal()
        try:
            # Check or onboard tenant for testing
            test_tenant = db.query(Tenant).filter(Tenant.tenant_id == "tenant_permission_test").first()
            if not test_tenant:
                test_tenant = Tenant(
                    tenant_id="tenant_permission_test",
                    name="Permission Test Org",
                    tenant_type="HOSPITAL"
                )
                db.add(test_tenant)
                db.commit()
                db.refresh(test_tenant)

            # 1. Doctor (has VIEW_PATIENT permission)
            doc_user = db.query(User).filter(User.email == "doc_perm@test.com").first()
            if not doc_user:
                doc_user = User(
                    email="doc_perm@test.com",
                    hashed_password="xyz",
                    full_name="Dr. Perm Tester",
                    role="doctor",
                    tenant_id="tenant_permission_test"
                )
                db.add(doc_user)

            # 2. Claim Processor (lacks VIEW_PATIENT permission)
            proc_user = db.query(User).filter(User.email == "proc_perm@test.com").first()
            if not proc_user:
                proc_user = User(
                    email="proc_perm@test.com",
                    hashed_password="xyz",
                    full_name="Processor Perm Tester",
                    role="claim_processor",
                    tenant_id="tenant_permission_test"
                )
                db.add(proc_user)
            db.commit()

            # Generate access tokens
            doc_token = create_access_token(subject="doc_perm@test.com", role="doctor")
            proc_token = create_access_token(subject="proc_perm@test.com", role="claim_processor")

            # 3. Test Authorized Request (Doctor should be allowed to list patients)
            headers_doc = {"Authorization": f"Bearer {doc_token}", "X-Tenant-ID": "tenant_permission_test"}
            response = test_client.get("/api/v1/patients/", headers=headers_doc)
            assert response.status_code == 200

            # 4. Test Unauthorized Request (Claim Processor should be blocked from listing patients)
            headers_proc = {"Authorization": f"Bearer {proc_token}", "X-Tenant-ID": "tenant_permission_test"}
            response = test_client.get("/api/v1/patients/", headers=headers_proc)
            assert response.status_code == 403
            assert "Required permission" in response.json()["detail"]

        finally:
            db.query(User).filter(User.tenant_id == "tenant_permission_test").delete()
            db.query(Tenant).filter(Tenant.tenant_id == "tenant_permission_test").delete()
            db.commit()
            db.close()
