from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.medical_report import MedicalReport
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.schemas.medical_report import MedicalReportCreate, MedicalReportUpdate, MedicalReportResponse
from app.middleware.auth import get_current_user, require_admin, require_role
from app.services.log import log_action

router = APIRouter(prefix="/api/reports", tags=["Medical Reports"])


@router.get("")
def list_reports(
    request: Request,
    patient_id: Optional[int] = Query(None),
    doctor_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(MedicalReport)
    if patient_id:
        query = query.filter(MedicalReport.patient_id == patient_id)
    if doctor_id:
        query = query.filter(MedicalReport.doctor_id == doctor_id)
    if search:
        term = f"%{search}%"
        query = query.filter(
            MedicalReport.symptoms.ilike(term)
            | MedicalReport.doctor_notes.ilike(term)
            | MedicalReport.diagnosis.ilike(term)
        )
    total = query.count()
    reports = query.order_by(MedicalReport.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "reports": reports, "skip": skip, "limit": limit}


@router.get("/{report_id}", response_model=MedicalReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("", response_model=MedicalReportResponse)
def create_report(
    request: Request,
    report_data: MedicalReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR)),
):
    patient = db.query(Patient).filter(Patient.id == report_data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    report = MedicalReport(**report_data.model_dump())
    report.doctor_id = current_user.id
    db.add(report)
    db.commit()
    db.refresh(report)
    log_action(
        db,
        user_id=current_user.id,
        username=current_user.username,
        action="REPORT_CREATED",
        resource="medical_report",
        resource_id=report.id,
        details=f"Created report for patient ID {report.patient_id}",
        ip_address=request.client.host if request.client else None,
    )
    return report


@router.put("/{report_id}", response_model=MedicalReportResponse)
def update_report(
    report_id: int,
    request: Request,
    report_data: MedicalReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR)),
):
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    for key, value in report_data.model_dump(exclude_unset=True).items():
        setattr(report, key, value)
    db.commit()
    db.refresh(report)
    log_action(
        db,
        user_id=current_user.id,
        username=current_user.username,
        action="REPORT_UPDATED",
        resource="medical_report",
        resource_id=report.id,
        details=f"Updated report ID {report.id}",
        ip_address=request.client.host if request.client else None,
    )
    return report


@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    log_action(
        db,
        user_id=current_user.id,
        username=current_user.username,
        action="REPORT_DELETED",
        resource="medical_report",
        resource_id=report.id,
        details=f"Deleted report ID {report.id}",
        ip_address=request.client.host if request.client else None,
    )
    db.delete(report)
    db.commit()
    return {"message": "Report deleted successfully"}
