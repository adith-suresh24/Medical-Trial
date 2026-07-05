from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.access_log import AccessLog
from app.models.user import User
from app.middleware.auth import get_current_user, require_admin
from app.services.log import log_action, search_logs
from datetime import datetime

router = APIRouter(prefix="/api/logs", tags=["Access Logs"])


@router.get("")
def list_logs(
    request: Request,
    search: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    resource: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.value not in ["admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    logs = search_logs(
        db,
        search=search,
        action=action,
        user_id=user_id,
        resource=resource,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
    total = db.query(AccessLog).count()
    return {"total": total, "logs": [log.__dict__ for log in logs], "skip": skip, "limit": limit}
