from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models.diagnosis import DiagnosisDatabase, Diagnosis
from app.models.patient import Patient
from app.models.user import User
from app.schemas.diagnosis import (
    DiagnosisDBCreate,
    DiagnosisDBResponse,
    DiagnosisCreate,
    DiagnosisResponse,
    SymptomMatchRequest,
    SymptomMatchResponse,
)
from app.middleware.auth import get_current_user, require_admin, require_role
from app.services.log import log_action

router = APIRouter(prefix="/api/diagnosis", tags=["Diagnosis"])


@router.get("/database")
def list_diagnosis_db(
    search: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(DiagnosisDatabase)
    if search:
        term = f"%{search}%"
        query = query.filter(
            DiagnosisDatabase.condition_name.ilike(term)
            | DiagnosisDatabase.symptoms.ilike(term)
        )
    if severity:
        query = query.filter(DiagnosisDatabase.severity == severity)
    total = query.count()
    conditions = query.order_by(DiagnosisDatabase.condition_name).offset(skip).limit(limit).all()
    return {"total": total, "conditions": conditions, "skip": skip, "limit": limit}


@router.post("/match")
def match_symptoms(
    request: SymptomMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    symptom_list = [s.strip().lower() for s in request.symptoms.split(",")]
    conditions = db.query(DiagnosisDatabase).all()
    matches = []

    for condition in conditions:
        condition_symptoms = [s.strip().lower() for s in condition.symptoms.split(",")]
        matched_symptoms = [s for s in symptom_list if s in condition_symptoms]
        match_percentage = len(matched_symptoms) / len(condition_symptoms) * 100 if condition_symptoms else 0

        if match_percentage >= 30:
            matches.append({
                "condition_name": condition.condition_name,
                "match_percentage": round(match_percentage, 1),
                "matched_symptoms": matched_symptoms,
                "severity": condition.severity,
                "description": condition.description,
                "recommendations": condition.recommendations,
                "common_treatments": condition.common_treatments,
                "icd_code": condition.icd_code,
            })

    matches.sort(key=lambda x: x["match_percentage"], reverse=True)
    return {"matches": matches, "total_matches": len(matches)}


@router.get("/patient/{patient_id}")
def get_patient_diagnoses(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    diagnoses = (
        db.query(Diagnosis)
        .filter(Diagnosis.patient_id == patient_id)
        .order_by(Diagnosis.created_at.desc())
        .all()
    )
    return diagnoses


@router.post("")
def create_diagnosis(
    request: Request,
    diagnosis_data: DiagnosisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = db.query(Patient).filter(Patient.id == diagnosis_data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    diagnosis = Diagnosis(**diagnosis_data.model_dump())
    diagnosis.doctor_id = current_user.id
    db.add(diagnosis)
    db.commit()
    db.refresh(diagnosis)
    log_action(
        db,
        user_id=current_user.id,
        username=current_user.username,
        action="DIAGNOSIS_CREATED",
        resource="diagnosis",
        resource_id=diagnosis.id,
        details=f"Diagnosis for patient ID {diagnosis.patient_id}: {diagnosis.condition_name}",
        ip_address=request.client.host if request.client else None,
    )
    return diagnosis
