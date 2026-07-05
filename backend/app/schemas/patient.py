from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date
    gender: str
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    admission_reason: Optional[str] = None
    department: Optional[str] = None
    ward_number: Optional[str] = None
    bed_number: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    admission_reason: Optional[str] = None
    department: Optional[str] = None
    ward_number: Optional[str] = None
    bed_number: Optional[str] = None
    status: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None


class PatientResponse(BaseModel):
    id: int
    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    admission_date: datetime
    admission_reason: Optional[str] = None
    department: Optional[str] = None
    ward_number: Optional[str] = None
    bed_number: Optional[str] = None
    status: str
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
