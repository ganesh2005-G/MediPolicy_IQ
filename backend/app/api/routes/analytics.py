from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import Claim, AuditLog, Tenant
from app.schemas.schemas import DashboardAnalyticsResponse, ClaimResponse, AuditLogResponse
from app.tenants.context import get_current_tenant

router = APIRouter(prefix="/analytics", tags=["Analytics & Executive Dashboard"])


@router.get("/dashboard", response_model=DashboardAnalyticsResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Retrieve executive metrics, claim auto-approval ratios, and fraud risk statistics for the active tenant."""
    claims = db.query(Claim).filter(Claim.tenant_id == tenant.tenant_id).all()

    total_claims = len(claims)
    total_billed = sum(c.total_billed_amount for c in claims)
    total_approved = sum(c.approved_amount for c in claims)

    fraud_flagged = sum(1 for c in claims if c.is_fraud_flagged)
    pending = sum(1 for c in claims if c.status in ["SUBMITTED", "UNDER_REVIEW"])
    auto_approved = sum(1 for c in claims if c.status == "APPROVED")

    auto_approval_rate = round((auto_approved / total_claims * 100.0), 1) if total_claims > 0 else 0.0

    recent_claims = db.query(Claim).filter(Claim.tenant_id == tenant.tenant_id).order_by(Claim.created_at.desc()).limit(10).all()

    return {
        "total_claims": total_claims,
        "total_billed_amount": total_billed,
        "total_approved_amount": total_approved,
        "auto_approval_rate": auto_approval_rate,
        "fraud_flagged_claims": fraud_flagged,
        "pending_claims": pending,
        "recent_claims": recent_claims
    }


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_system_audit_logs(
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Retrieve structured security audit logs for the active tenant."""
    return db.query(AuditLog).filter(AuditLog.tenant_id == tenant.tenant_id).order_by(AuditLog.timestamp.desc()).all()

