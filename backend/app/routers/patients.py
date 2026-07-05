from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.patient import Patient, AdmissionStatus
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from app.middleware.auth import get_current_user, require_admin, require_role
from app.services.log import log_action

router = APIRouter(prefix="/api/patients", tags=["Patients"])


def generate_patient_id(db: Session) -> str:
    count = db.query(Patient).count()
    return f"PTN{str(count + 1).zfill(6)}"


@router.get("")
def list_patients(
    request: Request,
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Patient)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Patient.first_name.ilike(search_term)
            | Patient.last_name.ilike(search_term)
            | Patient.patient_id.ilike(search_term)
            | Patient.phone.ilike(search_term)
        )
    if status:
        query = query.filter(Patient.status == status)
    if department:
        query = query.filter(Patient.department.ilike(f"%{department}%"))
    total = query.count()
    patients = query.order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "patients": patients, "skip": skip, "limit": limit}


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.post("", response_model=PatientResponse)
def create_patient(
    request: Request,
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = Patient(**patient_data.model_dump())
    patient.patient_id = generate_patient_id(db)
    patient.created_by = current_user.id
    db.add(patient)
    db.commit()
    db.refresh(patient)
    log_action(
        db,
        user_id=current_user.id,
        username=current_user.username,
        action="PATIENT_CREATED",
        resource="patient",
        resource_id=patient.id,
        details=f"Created patient: {patient.first_name} {patient.last_name}",
        ip_address=request.client.host if request.client else None,
    )
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    request: Request,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for key, value in patient_data.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    log_action(
        db,
        user_id=current_user.id,
        username=current_user.username,
        action="PATIENT_UPDATED",
        resource="patient",
        resource_id=patient.id,
        details=f"Updated patient: {patient.first_name} {patient.last_name}",
        ip_address=request.client.host if request.client else None,
    )
    return patient


@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    log_action(
        db,
        user_id=current_user.id,
        username=current_user.username,
        action="PATIENT_DELETED",
        resource="patient",
        resource_id=patient.id,
        details=f"Deleted patient: {patient.first_name} {patient.last_name}",
        ip_address=request.client.host if request.client else None,
    )
    db.delete(patient)
    db.commit()
    return {"message": "Patient deleted successfully"}
