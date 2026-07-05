import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.discharge_report import DischargeReport
from app.models.patient import Patient, AdmissionStatus
from app.models.user import User
from app.schemas.discharge_report import DischargeCreate, DischargeResponse
from app.middleware.auth import get_current_user, require_role
from app.services.log import log_action
from app.services.pdf import generate_discharge_pdf
from app.config import settings

router = APIRouter(prefix="/api/discharge", tags=["Discharge Reports"])


@router.get("")
def list_discharge_reports(
    request: Request,
    patient_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(DischargeReport)
    if patient_id:
        query = query.filter(DischargeReport.patient_id == patient_id)
    total = query.count()
    reports = query.order_by(DischargeReport.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "reports": reports, "skip": skip, "limit": limit}


@router.get("/{report_id}", response_model=DischargeResponse)
def get_discharge_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(DischargeReport).filter(DischargeReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Discharge report not found")
    return report


@router.post("", response_model=DischargeResponse)
def create_discharge_report(
    request: Request,
    discharge_data: DischargeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = db.query(Patient).filter(Patient.id == discharge_data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    report = DischargeReport(**discharge_data.model_dump())
    report.doctor_id = current_user.id
    db.add(report)
    db.commit()
    db.refresh(report)
    log_action(
        db,
        user_id=current_user.id,
        username=current_user.username,
        action="DISCHARGE_CREATED",
        resource="discharge_report",
        resource_id=report.id,
        details=f"Discharge report for patient ID {report.patient_id}",
        ip_address=request.client.host if request.client else None,
    )
    return report


@router.post("/{report_id}/generate-pdf")
def generate_pdf(
    report_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(DischargeReport).filter(DischargeReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Discharge report not found")
    patient = db.query(Patient).filter(Patient.id == report.patient_id).first()
    doctor = db.query(User).filter(User.id == report.doctor_id).first()

    pdf_path = generate_discharge_pdf(report, patient, doctor)
    report.pdf_path = pdf_path
    report.pdf_generated_at = datetime.utcnow()
    db.commit()

    log_action(
        db,
        user_id=current_user.id,
        username=current_user.username,
        action="PDF_GENERATED",
        resource="discharge_report",
        resource_id=report.id,
        details=f"PDF generated for discharge report ID {report.id}",
        ip_address=request.client.host if request.client else None,
    )

    return {"pdf_path": pdf_path, "message": "PDF generated successfully"}


@router.get("/{report_id}/download")
def download_pdf(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(DischargeReport).filter(DischargeReport.id == report_id).first()
    if not report or not report.pdf_path:
        raise HTTPException(status_code=404, detail="PDF not found")
    if not os.path.exists(report.pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")
    return FileResponse(
        report.pdf_path,
        media_type="application/pdf",
        filename=f"discharge_{report.patient_id}_{report.id}.pdf",
    )
