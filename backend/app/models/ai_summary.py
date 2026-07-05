from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class AISummary(Base):
    __tablename__ = "ai_summaries"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(
        Integer, ForeignKey("medical_reports.id"), nullable=False, index=True
    )
    patient_id = Column(
        Integer, ForeignKey("patients.id"), nullable=False, index=True
    )

    summary = Column(Text, nullable=True)
    risk_level = Column(String(20), nullable=True)
    recommendations = Column(Text, nullable=True)
    possible_conditions = Column(Text, nullable=True)
    raw_response = Column(Text, nullable=True)

    ai_model_used = Column(String(50), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    report = relationship("MedicalReport", back_populates="ai_summary")
    patient = relationship("Patient", back_populates="ai_summaries")
