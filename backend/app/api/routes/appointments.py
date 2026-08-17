import random
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from app.database.database import get_db
from app.models.models import Appointment

router = APIRouter(prefix="/appointments", tags=["Appointment Booking"])


class AppointmentCreate(BaseModel):
    patient_name: str
    doctor_name: str
    specialization: str
    appointment_date: str
    appointment_time: str


class AppointmentResponse(AppointmentCreate):
    id: int
    appointment_code: str
    status: str

    model_config = ConfigDict(from_attributes=True)


from app.tenants.context import get_current_tenant
from app.models.models import Tenant

class RescheduleRequest(BaseModel):
    appointment_date: str
    appointment_time: str


@router.post("/", response_model=AppointmentResponse)
def book_appointment(
    appointment_in: AppointmentCreate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Book a new doctor appointment with availability and double booking checks."""
    # 1. Validate operating hours (09:00 to 18:00)
    try:
        time_parts = appointment_in.appointment_time.split(":")
        hour = int(time_parts[0])
        if hour < 9 or hour >= 18:
            raise HTTPException(
                status_code=400,
                detail="Appointments can only be booked during standard operating hours (09:00 to 18:00)."
            )
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=400,
            detail="Invalid appointment time format. Must be HH:MM in 24-hour style."
        )

    # 2. Check double booking
    double_booked = db.query(Appointment).filter(
        Appointment.doctor_name == appointment_in.doctor_name,
        Appointment.appointment_date == appointment_in.appointment_date,
        Appointment.appointment_time == appointment_in.appointment_time,
        Appointment.tenant_id == tenant.tenant_id,
        Appointment.status.in_(["BOOKED", "CONFIRMED", "RESCHEDULED"])
    ).first()

    if double_booked:
        raise HTTPException(
            status_code=400,
            detail=f"Doctor '{appointment_in.doctor_name}' is already booked at {appointment_in.appointment_time} on {appointment_in.appointment_date}."
        )

    appointment_code = f"APT-{random.randint(10000, 99999)}"
    appointment = Appointment(
        appointment_code=appointment_code,
        patient_name=appointment_in.patient_name,
        doctor_name=appointment_in.doctor_name,
        specialization=appointment_in.specialization,
        appointment_date=appointment_in.appointment_date,
        appointment_time=appointment_in.appointment_time,
        status="BOOKED",
        tenant_id=tenant.tenant_id
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    # Log audit entry
    from app.database.audit import log_audit_action
    log_audit_action(
        db=db,
        tenant_id=tenant.tenant_id,
        action="BOOK_APPOINTMENT",
        entity_type="APPOINTMENT",
        entity_id=appointment.id,
        details=f"Booked appointment {appointment.appointment_code} for {appointment.patient_name} with {appointment.doctor_name}."
    )

    return appointment


@router.get("/", response_model=List[AppointmentResponse])
def list_appointments(
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """List all scheduled appointments for the active tenant."""
    return db.query(Appointment).filter(Appointment.tenant_id == tenant.tenant_id).order_by(Appointment.created_at.desc()).all()


@router.put("/{appointment_id}/reschedule", response_model=AppointmentResponse)
def reschedule_appointment(
    appointment_id: int,
    res_in: RescheduleRequest,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Reschedule an existing appointment subject to double-booking prevention."""
    appt = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.tenant_id == tenant.tenant_id
    ).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found.")

    # Validate operating hours
    try:
        hour = int(res_in.appointment_time.split(":")[0])
        if hour < 9 or hour >= 18:
            raise HTTPException(status_code=400, detail="OPD hours are 09:00 to 18:00.")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid HH:MM format.")

    # Check double booking
    double_booked = db.query(Appointment).filter(
        Appointment.doctor_name == appt.doctor_name,
        Appointment.appointment_date == res_in.appointment_date,
        Appointment.appointment_time == res_in.appointment_time,
        Appointment.tenant_id == tenant.tenant_id,
        Appointment.id != appointment_id,
        Appointment.status.in_(["BOOKED", "CONFIRMED", "RESCHEDULED"])
    ).first()

    if double_booked:
        raise HTTPException(
            status_code=400,
            detail=f"Doctor is already booked at {res_in.appointment_time} on {res_in.appointment_date}."
        )

    appt.appointment_date = res_in.appointment_date
    appt.appointment_time = res_in.appointment_time
    appt.status = "RESCHEDULED"
    db.commit()
    db.refresh(appt)

    # Log audit entry
    from app.database.audit import log_audit_action
    log_audit_action(
        db=db,
        tenant_id=tenant.tenant_id,
        action="RESCHEDULE_APPOINTMENT",
        entity_type="APPOINTMENT",
        entity_id=appt.id,
        details=f"Rescheduled appointment {appt.appointment_code} to {appt.appointment_date} at {appt.appointment_time}."
    )

    return appt


@router.put("/{appointment_id}/status", response_model=AppointmentResponse)
def update_appointment_status(
    appointment_id: int,
    status: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Update appointment status (BOOKED, CONFIRMED, COMPLETED, CANCELLED, RESCHEDULED, NO_SHOW)."""
    appt = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.tenant_id == tenant.tenant_id
    ).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found.")

    valid_states = ["BOOKED", "CONFIRMED", "COMPLETED", "CANCELLED", "RESCHEDULED", "NO_SHOW"]
    if status not in valid_states:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_states}")

    old_status = appt.status
    appt.status = status
    db.commit()
    db.refresh(appt)

    # Log audit entry
    from app.database.audit import log_audit_action
    log_audit_action(
        db=db,
        tenant_id=tenant.tenant_id,
        action="UPDATE_APPOINTMENT_STATUS",
        entity_type="APPOINTMENT",
        entity_id=appt.id,
        details=f"Updated appointment {appt.appointment_code} status from {old_status} to {status}."
    )

    return appt


