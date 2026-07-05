from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.schemas.user import UserCreate


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    if user.is_locked:
        return None
    user.last_login = datetime.utcnow()
    user.failed_login_attempts = 0
    db.commit()
    return user


def create_user(db: Session, user_data: UserCreate):
    hashed = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed,
        full_name=user_data.full_name,
        role=UserRole(user_data.role) if hasattr(UserRole, user_data.role.upper()) else UserRole.STAFF,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_all_users(db: Session):
    return db.query(User).all()


def update_user_role(db: Session, user_id: int, role: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.role = UserRole(role)
        db.commit()
        db.refresh(user)
    return user


def lock_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_locked = True
        db.commit()
    return user


def unlock_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_locked = False
        user.failed_login_attempts = 0
        db.commit()
    return user
