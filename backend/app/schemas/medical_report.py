from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MedicalReportCreate(BaseModel):
    patient_id: int
    symptoms: str = Field(..., min_length=1)
    observations: Optional[str] = None
    doctor_notes: Optional[str] = None
    treatment: Optional[str] = None
    diagnosis: Optional[str] = None
    prescribed_medications: Optional[str] = None
    follow_up_date: Optional[datetime] = None


class MedicalReportUpdate(BaseModel):
    symptoms: Optional[str] = None
    observations: Optional[str] = None
    doctor_notes: Optional[str] = None
    treatment: Optional[str] = None
    diagnosis: Optional[str] = None
    prescribed_medications: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    is_finalized: Optional[int] = None


class MedicalReportResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    symptoms: str
    observations: Optional[str] = None
    doctor_notes: Optional[str] = None
    treatment: Optional[str] = None
    diagnosis: Optional[str] = None
    prescribed_medications: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    is_finalized: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
