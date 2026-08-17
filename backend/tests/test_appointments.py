from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.models.models import Appointment, Tenant, User
from app.core.security import create_access_token

client = TestClient(app)


def test_appointment_scheduling_engine():
    """Verify that booking prevents double bookings, respects operating hours, and isolates tenants."""
    with TestClient(app) as test_client:
        db = SessionLocal()
        try:
            # 1. Onboard two testing tenants
            t1 = db.query(Tenant).filter(Tenant.tenant_id == "hosp_apt_t1").first()
            if not t1:
                t1 = Tenant(tenant_id="hosp_apt_t1", name="Hosp T1", tenant_type="HOSPITAL")
                db.add(t1)

            t2 = db.query(Tenant).filter(Tenant.tenant_id == "hosp_apt_t2").first()
            if not t2:
                t2 = Tenant(tenant_id="hosp_apt_t2", name="Hosp T2", tenant_type="HOSPITAL")
                db.add(t2)
            db.commit()

            admin_token1 = create_access_token(subject="admin1@test.com", role="admin")
            admin_token2 = create_access_token(subject="admin2@test.com", role="admin")

            # 2. Test booking outside operating hours (OPD hours are 09:00 to 18:00)
            bad_time_payload = {
                "patient_name": "John Doe",
                "doctor_name": "Dr. Sarah Jenkins",
                "specialization": "Cardiology",
                "appointment_date": "2026-09-01",
                "appointment_time": "08:00"  # Before 9 AM
            }
            headers_t1 = {"Authorization": f"Bearer {admin_token1}", "X-Tenant-ID": "hosp_apt_t1"}
            res = test_client.post("/api/v1/appointments/", json=bad_time_payload, headers=headers_t1)
            assert res.status_code == 400
            assert "operating hours" in res.json()["detail"]

            # 3. Book a valid appointment
            good_payload = {
                "patient_name": "John Doe",
                "doctor_name": "Dr. Sarah Jenkins",
                "specialization": "Cardiology",
                "appointment_date": "2026-09-01",
                "appointment_time": "10:30"
            }
            res = test_client.post("/api/v1/appointments/", json=good_payload, headers=headers_t1)
            assert res.status_code == 200
            appt_id = res.json()["id"]

            # 4. Attempt to double book the same doctor, date, and time under same tenant (should fail)
            res = test_client.post("/api/v1/appointments/", json=good_payload, headers=headers_t1)
            assert res.status_code == 400
            assert "already booked" in res.json()["detail"]

            # 5. Book same doctor/date/time under a DIFFERENT tenant (should succeed due to tenant isolation)
            headers_t2 = {"Authorization": f"Bearer {admin_token2}", "X-Tenant-ID": "hosp_apt_t2"}
            res = test_client.post("/api/v1/appointments/", json=good_payload, headers=headers_t2)
            assert res.status_code == 200

            # 6. Test reschedule to an available slot
            reschedule_payload = {
                "appointment_date": "2026-09-01",
                "appointment_time": "14:00"
            }
            res = test_client.put(f"/api/v1/appointments/{appt_id}/reschedule", json=reschedule_payload, headers=headers_t1)
            assert res.status_code == 200
            assert res.json()["status"] == "RESCHEDULED"
            assert res.json()["appointment_time"] == "14:00"

            # 7. Test status lifecycle update
            res = test_client.put(f"/api/v1/appointments/{appt_id}/status?status=CANCELLED", headers=headers_t1)
            assert res.status_code == 200
            assert res.json()["status"] == "CANCELLED"

        finally:
            db.query(Appointment).filter(Appointment.tenant_id.in_(["hosp_apt_t1", "hosp_apt_t2"])).delete()
            db.query(Tenant).filter(Tenant.tenant_id.in_(["hosp_apt_t1", "hosp_apt_t2"])).delete()
            db.commit()
            db.close()
