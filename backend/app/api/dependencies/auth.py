from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.core.security import decode_access_token
from app.models.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to retrieve and validate current logged in user from JWT."""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email: str = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user


from app.core.constants import ROLE_PERMISSIONS

def require_role(allowed_roles: list[str]):
    """Role-Based Access Control (RBAC) dependency wrapper."""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for role '{current_user.role}'. Required: {allowed_roles}"
            )
        return current_user
    return role_checker


def requires_permission(required_permission: str):
    """Permission-Based Access Control (PBAC) dependency wrapper."""
    def permission_checker(current_user: User = Depends(get_current_user)):
        user_perms = ROLE_PERMISSIONS.get(current_user.role, [])
        if required_permission not in user_perms and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: '{required_permission}'"
            )
        return current_user
    return permission_checker

