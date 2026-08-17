from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import Tenant


def get_request_tenant_id(x_tenant_id: str = Header(None, alias="X-Tenant-ID")) -> str:
    """
    Dependency to extract tenant identifier from the custom 'X-Tenant-ID' request header.
    Falls back gracefully to a default tenant or throws an error.
    """
    if not x_tenant_id:
        # For open/public/development endpoints, we can fallback to default admin space
        return "system_admin"
    return x_tenant_id


def get_current_tenant(
    tenant_id: str = Depends(get_request_tenant_id),
    db: Session = Depends(get_db)
) -> Tenant:
    """
    Dependency to look up and validate the active Tenant structure based on request context.
    """
    if tenant_id == "system_admin":
        # System Admin dummy tenant config
        return Tenant(tenant_id="system_admin", name="System Administration", tenant_type="SYSTEM")
        
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requested tenant '{tenant_id}' is invalid or does not exist."
        )
    if not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The requested organization tenant is currently suspended."
        )
    return tenant
