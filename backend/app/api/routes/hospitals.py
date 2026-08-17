from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.database import get_db
from app.models.models import Hospital, Doctor
from app.schemas.schemas import HospitalCreate, HospitalResponse
from app.services.medical_coding import ICD10_DATABASE, CPT_DATABASE

router = APIRouter(prefix="/hospitals", tags=["Hospital & Doctor Management"])


class DoctorCreate(BaseModel):
    doctor_code: str
    full_name: str
    specialization: str
    qualification: Optional[str] = "MD / MS"
    department: str
    hospital_name: Optional[str] = "Metro General Hospital"
    phone: Optional[str] = None
    email: Optional[str] = None


from pydantic import BaseModel, ConfigDict
from app.tenants.context import get_current_tenant
from app.models.models import Tenant

class DoctorResponse(DoctorCreate):
    id: int
    is_on_duty: bool

    model_config = ConfigDict(from_attributes=True)


@router.post("/", response_model=HospitalResponse)
def create_hospital(
    hospital_in: HospitalCreate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Create a new hospital facility record."""
    existing = db.query(Hospital).filter(
        Hospital.hospital_code == hospital_in.hospital_code,
        Hospital.tenant_id == tenant.tenant_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Hospital code already exists.")

    hospital = Hospital(**hospital_in.model_dump(), tenant_id=tenant.tenant_id)
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital


@router.get("/", response_model=List[HospitalResponse])
def list_hospitals(
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """List registered hospitals for the active tenant."""
    return db.query(Hospital).filter(Hospital.tenant_id == tenant.tenant_id).all()


@router.get("/doctors", response_model=List[DoctorResponse])
def list_doctors(
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """List hospital doctors and medical specialists for the active tenant."""
    return db.query(Doctor).filter(Doctor.tenant_id == tenant.tenant_id).all()


@router.post("/doctors", response_model=DoctorResponse)
def add_doctor(
    doc_in: DoctorCreate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Add a new doctor to the hospital directory under the active tenant."""
    existing = db.query(Doctor).filter(
        Doctor.doctor_code == doc_in.doctor_code,
        Doctor.tenant_id == tenant.tenant_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Doctor code already exists.")

    doc = Doctor(**doc_in.model_dump(), tenant_id=tenant.tenant_id)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc



@router.get("/diseases")
def list_diseases_and_diagnoses(query: Optional[str] = Query(None)):
    """Searchable database of hospital diseases, ICD-10 diagnosis codes, procedure categories, and standard INR treatment fees."""
    results = []
    for code, info in ICD10_DATABASE.items():
        if not query or query.lower() in code.lower() or query.lower() in info["description"].lower() or query.lower() in info["category"].lower():
            results.append({
                "icd_code": f"ICD10-{code}",
                "disease_name": info["description"],
                "category": info["category"],
                "standard_length_of_stay": f"{info['standard_length_of_stay_days']} Days",
                "estimated_cost_inr": "₹35,000 - ₹1,50,000"
            })
    return results
