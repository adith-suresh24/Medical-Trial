from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    symptoms = Column(Text, nullable=False)
    observations = Column(Text, nullable=True)
    doctor_notes = Column(Text, nullable=True)
    treatment = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    prescribed_medications = Column(Text, nullable=True)
    follow_up_date = Column(DateTime, nullable=True)

    is_finalized = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = relationship("Patient", back_populates="medical_reports")
    doctor = relationship("User", back_populates="medical_reports")
    ai_summary = relationship(
        "AISummary", back_populates="report", uselist=False, cascade="all, delete-orphan"
    )
