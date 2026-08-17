from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import Claim
from app.schemas.schemas import DashboardAnalyticsResponse, ClaimResponse

router = APIRouter(prefix="/analytics", tags=["Analytics & Executive Dashboard"])


@router.get("/dashboard", response_model=DashboardAnalyticsResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Retrieve executive metrics, claim auto-approval ratios, and fraud risk statistics."""
    claims = db.query(Claim).all()

    total_claims = len(claims)
    total_billed = sum(c.total_billed_amount for c in claims)
    total_approved = sum(c.approved_amount for c in claims)

    fraud_flagged = sum(1 for c in claims if c.is_fraud_flagged)
    pending = sum(1 for c in claims if c.status in ["SUBMITTED", "UNDER_REVIEW"])
    auto_approved = sum(1 for c in claims if c.status == "APPROVED")

    auto_approval_rate = round((auto_approved / total_claims * 100.0), 1) if total_claims > 0 else 0.0

    recent_claims = db.query(Claim).order_by(Claim.created_at.desc()).limit(10).all()

    return {
        "total_claims": total_claims,
        "total_billed_amount": total_billed,
        "total_approved_amount": total_approved,
        "auto_approval_rate": auto_approval_rate,
        "fraud_flagged_claims": fraud_flagged,
        "pending_claims": pending,
        "recent_claims": recent_claims
    }
