from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.security import decode_access_token
from app.models.user import User, UserRole

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


def require_role(required_role: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):
        role_priority = {
            UserRole.ADMIN: 3,
            UserRole.DOCTOR: 2,
            UserRole.STAFF: 1,
        }
        if role_priority.get(current_user.role, 0) < role_priority.get(required_role, 0):
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker


def require_admin(current_user: User = Depends(require_role(UserRole.ADMIN))):
    return current_user
