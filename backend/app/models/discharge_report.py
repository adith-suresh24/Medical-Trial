from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base


class DischargeReport(Base):
    __tablename__ = "discharge_reports"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    diagnosis = Column(Text, nullable=False)
    treatment_summary = Column(Text, nullable=False)
    medications_prescribed = Column(Text, nullable=True)
    follow_up_instructions = Column(Text, nullable=True)
    dietary_recommendations = Column(Text, nullable=True)
    activity_restrictions = Column(Text, nullable=True)
    additional_notes = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)

    discharge_date = Column(Date, nullable=False)
    follow_up_date = Column(Date, nullable=True)

    pdf_path = Column(String(500), nullable=True)
    pdf_generated_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = relationship("Patient", back_populates="discharge_reports")
    doctor = relationship("User", back_populates="discharge_reports")
