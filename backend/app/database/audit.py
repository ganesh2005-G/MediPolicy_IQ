from sqlalchemy.orm import Session
from app.models.models import AuditLog

def log_audit_action(
    db: Session,
    tenant_id: str,
    action: str,
    entity_type: str,
    entity_id: str = None,
    user_email: str = "system",
    details: str = None
):
    """Utility helper to record a structured audit log entry in the database under tenant scope."""
    audit = AuditLog(
        tenant_id=tenant_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        user_email=user_email,
        details=details
    )
    db.add(audit)
    db.commit()
