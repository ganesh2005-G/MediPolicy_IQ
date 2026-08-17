from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import Tenant, TenantConfiguration, User
from app.schemas.schemas import TenantCreate, TenantResponse
from app.core.security import get_password_hash
from app.tenants.context import get_current_tenant

router = APIRouter(prefix="/tenants", tags=["Multi-Tenancy & Onboarding"])


@router.get("/test-context")
def test_tenant_context(tenant = Depends(get_current_tenant)):
    """Debug endpoint to verify header-based tenant context resolution."""
    return {"tenant_id": tenant.tenant_id, "name": tenant.name}



@router.post("/onboard", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def onboard_tenant(tenant_in: TenantCreate, db: Session = Depends(get_db)):
    """
    Onboard a brand new hospital, insurance carrier, or clinic.
    Sets up branding configurations and registers the Tenant Administrator profile.
    """
    # 1. Check if tenant_id already onboarded
    existing_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_in.tenant_id).first()
    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization with tenant_id '{tenant_in.tenant_id}' is already onboarded."
        )

    # 2. Check if admin email already registered
    existing_user = db.query(User).filter(User.email == tenant_in.admin_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with admin email '{tenant_in.admin_email}' is already registered."
        )

    # 3. Create Tenant
    tenant = Tenant(
        tenant_id=tenant_in.tenant_id,
        name=tenant_in.name,
        tenant_type=tenant_in.tenant_type.upper(),
        primary_color=tenant_in.primary_color,
        secondary_color=tenant_in.secondary_color,
        logo_url=tenant_in.logo_url
    )
    db.add(tenant)
    db.commit() # Commit tenant first so foreign key constraints are satisfied
    db.refresh(tenant)

    # 4. Create Tenant Configuration
    config = TenantConfiguration(
        tenant_id=tenant_in.tenant_id,
        features=tenant_in.features or {"claims": True, "ocr": True, "ai_assistant": True},
        ai_config=tenant_in.ai_config or {
            "assistant_name": f"{tenant_in.name} AI",
            "tone": "professional",
            "instructions": f"Help user navigate policies/records for {tenant_in.name}."
        },
        operating_hours=tenant_in.operating_hours or {
            "opd_start": "09:00",
            "opd_end": "18:00",
            "emergency_service": True
        }
    )
    db.add(config)

    # 5. Create Tenant Admin user
    admin_user = User(
        email=tenant_in.admin_email,
        hashed_password=get_password_hash(tenant_in.admin_password),
        full_name=tenant_in.admin_full_name,
        role=tenant_in.admin_role or "admin",
        tenant_id=tenant_in.tenant_id
    )
    db.add(admin_user)
    db.commit()

    # 6. Log Audit Action
    from app.database.audit import log_audit_action
    log_audit_action(
        db=db,
        tenant_id=tenant_in.tenant_id,
        action="ONBOARD_ORGANIZATION",
        entity_type="TENANT",
        entity_id=tenant_in.tenant_id,
        user_email=tenant_in.admin_email,
        details=f"Onboarded organization '{tenant_in.name}' of type {tenant_in.tenant_type}."
    )

    return tenant

