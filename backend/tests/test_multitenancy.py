from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.models.models import Tenant, TenantConfiguration, User

def test_tenant_onboarding():
    """Verify that onboarding endpoint correctly registers tenants, configurations, and admin users."""
    with TestClient(app) as client:
        payload = {
            "tenant_id": "test_hospital_xyz",
            "name": "XYZ Community Hospital",
            "tenant_type": "HOSPITAL",
            "primary_color": "#ff0000",
            "secondary_color": "#00ff00",
            "admin_email": "admin@xyzcommunity.org",
            "admin_password": "XYZPassword123!",
            "admin_full_name": "Dr. Alex Carter"
        }
        
        response = client.post("/api/v1/tenants/onboard", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["tenant_id"] == "test_hospital_xyz"
        assert data["name"] == "XYZ Community Hospital"
        assert data["primary_color"] == "#ff0000"

        # Query DB to check objects are present
        db = SessionLocal()
        try:
            tenant = db.query(Tenant).filter(Tenant.tenant_id == "test_hospital_xyz").first()
            assert tenant is not None
            assert tenant.tenant_type == "HOSPITAL"

            config = db.query(TenantConfiguration).filter(TenantConfiguration.tenant_id == "test_hospital_xyz").first()
            assert config is not None
            assert config.ai_config["assistant_name"] == "XYZ Community Hospital AI"

            admin = db.query(User).filter(User.email == "admin@xyzcommunity.org").first()
            assert admin is not None
            assert admin.tenant_id == "test_hospital_xyz"
            assert admin.role == "admin"
        finally:
            # Clean up database after test
            db.query(User).filter(User.tenant_id == "test_hospital_xyz").delete()
            db.query(TenantConfiguration).filter(TenantConfiguration.tenant_id == "test_hospital_xyz").delete()
            db.query(Tenant).filter(Tenant.tenant_id == "test_hospital_xyz").delete()
            db.commit()
            db.close()


def test_tenant_header_context():
    """Verify context helper validation behaviors for X-Tenant-ID header."""
    with TestClient(app) as client:
        # 1. Test missing header context defaults to system_admin context
        response = client.get("/api/v1/tenants/test-context")
        assert response.status_code == 200
        assert response.json()["tenant_id"] == "system_admin"

        # 2. Test valid onboarded tenant header (seeded in lifespan)
        headers = {"X-Tenant-ID": "hospital_001"}
        response = client.get("/api/v1/tenants/test-context", headers=headers)
        assert response.status_code == 200
        assert response.json()["tenant_id"] == "hospital_001"
        assert response.json()["name"] == "Medicare Central Hospital"
        
        # 3. Test invalid tenant header raises 404
        headers = {"X-Tenant-ID": "non_existent_tenant_id_abc"}
        response = client.get("/api/v1/tenants/test-context", headers=headers)
        assert response.status_code == 404
        assert "invalid or does not exist" in response.json()["detail"]
