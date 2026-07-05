from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import (
    LoginRequest,
    Token,
    UserCreate,
    UserResponse,
    ChangePasswordRequest,
)
from app.services.auth import (
    authenticate_user,
    create_user,
    get_user_by_id,
    get_all_users,
)
from app.middleware.auth import get_current_user, require_admin
from app.models.user import User, UserRole
from app.services.log import log_action
from app.utils.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        log_action(
            db,
            user_id=None,
            username=login_data.username,
            action="LOGIN_FAILED",
            resource="auth",
            details="Invalid credentials",
            ip_address=request.client.host if request.client else None,
            status="failed",
        )
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(
        data={"user_id": user.id, "role": user.role.value, "sub": user.username}
    )

    log_action(
        db,
        user_id=user.id,
        username=user.username,
        action="LOGIN",
        resource="auth",
        details="User logged in",
        ip_address=request.client.host if request.client else None,
    )

    return Token(
        access_token=access_token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
            last_login=user.last_login,
            created_at=user.created_at,
        ),
    )


@router.post("/register", response_model=UserResponse)
def register(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    existing = (
        db.query(User)
        .filter((User.username == user_data.username) | (User.email == user_data.email))
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    user = create_user(db, user_data)
    log_action(
        db,
        user_id=current_user.id,
        username=current_user.username,
        action="USER_CREATED",
        resource="user",
        resource_id=user.id,
        details=f"Created user: {user.username}",
        ip_address=request.client.host if request.client else None,
    )
    return user


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return get_all_users(db)


@router.put("/change-password")
def change_password(
    request: Request,
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    log_action(
        db,
        user_id=current_user.id,
        username=current_user.username,
        action="PASSWORD_CHANGED",
        resource="auth",
        details="User changed password",
        ip_address=request.client.host if request.client else None,
    )
    return {"message": "Password updated successfully"}


@router.post("/logout")
def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log_action(
        db,
        user_id=current_user.id,
        username=current_user.username,
        action="LOGOUT",
        resource="auth",
        details="User logged out",
        ip_address=request.client.host if request.client else None,
    )
    return {"message": "Logged out successfully"}
