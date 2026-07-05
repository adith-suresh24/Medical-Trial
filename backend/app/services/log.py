from sqlalchemy.orm import Session
from app.models.access_log import AccessLog
from datetime import datetime


def log_action(
    db: Session,
    user_id: int = None,
    username: str = None,
    action: str = None,
    resource: str = None,
    resource_id: int = None,
    details: str = None,
    ip_address: str = None,
    user_agent: str = None,
    status: str = "success",
):
    log = AccessLog(
        user_id=user_id,
        username=username,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status,
        created_at=datetime.utcnow(),
    )
    db.add(log)
    db.commit()


def search_logs(
    db: Session,
    search: str = None,
    action: str = None,
    user_id: int = None,
    resource: str = None,
    start_date: str = None,
    end_date: str = None,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(AccessLog)
    if search:
        query = query.filter(
            AccessLog.details.contains(search)
            | AccessLog.username.contains(search)
            | AccessLog.action.contains(search)
        )
    if action:
        query = query.filter(AccessLog.action == action)
    if user_id:
        query = query.filter(AccessLog.user_id == user_id)
    if resource:
        query = query.filter(AccessLog.resource == resource)
    if start_date:
        query = query.filter(AccessLog.created_at >= start_date)
    if end_date:
        query = query.filter(AccessLog.created_at <= end_date)
    return query.order_by(AccessLog.created_at.desc()).offset(skip).limit(limit).all()
