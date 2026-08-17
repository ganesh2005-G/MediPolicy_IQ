from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import Patient
from app.schemas.schemas import PatientCreate, PatientResponse

from app.api.dependencies.auth import requires_permission
from app.core.constants import Permission

from app.tenants.context import get_current_tenant
from app.models.models import Tenant

router = APIRouter(prefix="/patients", tags=["Patient Management"])


@router.post("/", response_model=PatientResponse)
def create_patient(
    patient_in: PatientCreate,
    db: Session = Depends(get_db),
    current_user = Depends(requires_permission(Permission.EDIT_PATIENT)),
    tenant: Tenant = Depends(get_current_tenant)
):
    existing = db.query(Patient).filter(
        Patient.patient_code == patient_in.patient_code,
        Patient.tenant_id == tenant.tenant_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Patient with code already exists.")

    patient = Patient(**patient_in.model_dump(), tenant_id=tenant.tenant_id)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/", response_model=List[PatientResponse])
def list_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(requires_permission(Permission.VIEW_PATIENT)),
    tenant: Tenant = Depends(get_current_tenant)
):
    return db.query(Patient).filter(Patient.tenant_id == tenant.tenant_id).offset(skip).limit(limit).all()


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(requires_permission(Permission.VIEW_PATIENT)),
    tenant: Tenant = Depends(get_current_tenant)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.tenant_id == tenant.tenant_id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")
    return patient


