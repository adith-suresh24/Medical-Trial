from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class DischargeCreate(BaseModel):
    patient_id: int
    diagnosis: str
    treatment_summary: str
    medications_prescribed: Optional[str] = None
    follow_up_instructions: Optional[str] = None
    dietary_recommendations: Optional[str] = None
    activity_restrictions: Optional[str] = None
    additional_notes: Optional[str] = None
    ai_summary: Optional[str] = None
    discharge_date: date
    follow_up_date: Optional[date] = None


class DischargeResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    diagnosis: str
    treatment_summary: str
    medications_prescribed: Optional[str] = None
    follow_up_instructions: Optional[str] = None
    dietary_recommendations: Optional[str] = None
    activity_restrictions: Optional[str] = None
    additional_notes: Optional[str] = None
    ai_summary: Optional[str] = None
    discharge_date: date
    follow_up_date: Optional[date] = None
    pdf_path: Optional[str] = None
    pdf_generated_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
