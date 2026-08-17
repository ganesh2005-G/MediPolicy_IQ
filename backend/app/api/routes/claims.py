from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import Claim, AuditLog
from app.schemas.schemas import ClaimCreate, ClaimResponse
from app.services.claim_service import ClaimService

router = APIRouter(prefix="/claims", tags=["Claim Adjudication & Processing"])


@router.post("/", response_model=ClaimResponse)
def submit_and_process_claim(claim_in: ClaimCreate, db: Session = Depends(get_db)):
    """Submit a claim for automated AI adjudication, COB calculation, and fraud analysis."""
    try:
        claim = ClaimService.process_and_create_claim(db=db, claim_in=claim_in)
        return claim
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.get("/", response_model=List[ClaimResponse])
def list_claims(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all submitted claims with adjudication status and decisions."""
    return db.query(Claim).order_by(Claim.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/patient/{patient_id}", response_model=List[ClaimResponse])
def get_patient_claims(patient_id: int, db: Session = Depends(get_db)):
    """Get claims belonging to a specific patient."""
    return db.query(Claim).filter(Claim.patient_id == patient_id).order_by(Claim.created_at.desc()).all()


@router.get("/{claim_id}", response_model=ClaimResponse)
def get_claim_detail(claim_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed adjudication breakdown for a specific claim."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found.")
    return claim


@router.put("/{claim_id}/status", response_model=ClaimResponse)
def update_claim_status(
    claim_id: int,
    status: str = Body(..., embed=True),
    decision_notes: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db)
):
    """Processor endpoint to manually APPROVE or REJECT a claim."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found.")

    valid_statuses = ["APPROVED", "REJECTED", "PARTIALLY_APPROVED", "UNDER_REVIEW", "FLAGGED_FRAUD"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")

    claim.status = status
    if status == "REJECTED":
        claim.approved_amount = 0.0
        claim.patient_payable = claim.total_billed_amount

    if decision_notes:
        explanation = claim.decision_explanation or {}
        explanation["processor_notes"] = decision_notes
        claim.decision_explanation = explanation

    audit = AuditLog(
        user_email="processor",
        action="MANUAL_STATUS_UPDATE",
        entity_type="CLAIM",
        entity_id=str(claim.id),
        details=f"Updated claim status to {status} with notes: {decision_notes}"
    )
    db.add(audit)
    db.commit()
    db.refresh(claim)
    return claim
