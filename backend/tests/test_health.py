from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_liveness_probe():
    """Verify that liveness probe endpoint returns UP and app info."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert "service" in data
    assert "version" in data


def test_health_readiness_probe():
    """Verify that readiness probe endpoint performs database and subsystem checks."""
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert "details" in data
    assert "database" in data["details"]
    assert data["details"]["database"]["status"] == "CONNECTED"
