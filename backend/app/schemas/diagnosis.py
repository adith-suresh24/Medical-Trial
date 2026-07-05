from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DiagnosisDBCreate(BaseModel):
    condition_name: str = Field(..., min_length=1, max_length=200)
    symptoms: str = Field(..., min_length=1)
    severity: str = Field(..., min_length=1)
    description: Optional[str] = None
    recommendations: Optional[str] = None
    common_treatments: Optional[str] = None
    icd_code: Optional[str] = None


class DiagnosisDBResponse(BaseModel):
    id: int
    condition_name: str
    symptoms: str
    severity: str
    description: Optional[str] = None
    recommendations: Optional[str] = None
    common_treatments: Optional[str] = None
    icd_code: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DiagnosisCreate(BaseModel):
    patient_id: int
    condition_name: str = Field(..., min_length=1)
    icd_code: Optional[str] = None
    severity: Optional[str] = None
    symptoms: Optional[str] = None
    diagnosis_notes: Optional[str] = None
    recommendations: Optional[str] = None
    is_confirmed: Optional[int] = 0


class DiagnosisResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    condition_name: str
    icd_code: Optional[str] = None
    severity: Optional[str] = None
    symptoms: Optional[str] = None
    diagnosis_notes: Optional[str] = None
    recommendations: Optional[str] = None
    is_confirmed: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SymptomMatchRequest(BaseModel):
    symptoms: str


class SymptomMatchResponse(BaseModel):
    condition_name: str
    match_percentage: float
    matched_symptoms: list
    severity: str
    description: Optional[str] = None
    recommendations: Optional[str] = None
    common_treatments: Optional[str] = None
    icd_code: Optional[str] = None
