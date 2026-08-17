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


@router.post("/", response_model=AppointmentResponse)
def book_appointment(appointment_in: AppointmentCreate, db: Session = Depends(get_db)):
    """Book a new doctor appointment."""
    appointment_code = f"APT-{random.randint(10000, 99999)}"
    appointment = Appointment(
        appointment_code=appointment_code,
        patient_name=appointment_in.patient_name,
        doctor_name=appointment_in.doctor_name,
        specialization=appointment_in.specialization,
        appointment_date=appointment_in.appointment_date,
        appointment_time=appointment_in.appointment_time,
        status="BOOKED"
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/", response_model=List[AppointmentResponse])
def list_appointments(db: Session = Depends(get_db)):
    """List all scheduled appointments."""
    return db.query(Appointment).order_by(Appointment.created_at.desc()).all()
