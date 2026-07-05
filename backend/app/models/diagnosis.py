from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class DiagnosisDatabase(Base):
    __tablename__ = "diagnosis_database"

    id = Column(Integer, primary_key=True, index=True)
    condition_name = Column(String(200), nullable=False, index=True)
    symptoms = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    common_treatments = Column(Text, nullable=True)
    icd_code = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    condition_name = Column(String(200), nullable=False)
    icd_code = Column(String(20), nullable=True)
    severity = Column(String(20), nullable=True)
    symptoms = Column(Text, nullable=True)
    diagnosis_notes = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    is_confirmed = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = relationship("Patient", back_populates="diagnoses")
    doctor = relationship("User", back_populates="diagnoses")
