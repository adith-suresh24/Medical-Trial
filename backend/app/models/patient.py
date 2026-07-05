from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Date, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class BloodGroup(str, enum.Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class AdmissionStatus(str, enum.Enum):
    ACTIVE = "active"
    DISCHARGED = "discharged"
    TRANSFERRED = "transferred"


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(20), unique=True, nullable=False, index=True)

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    blood_group = Column(Enum(BloodGroup), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)

    admission_date = Column(DateTime, default=datetime.utcnow)
    admission_reason = Column(Text, nullable=True)
    department = Column(String(100), nullable=True)
    ward_number = Column(String(20), nullable=True)
    bed_number = Column(String(20), nullable=True)
    status = Column(Enum(AdmissionStatus), default=AdmissionStatus.ACTIVE)

    medical_history = Column(Text, nullable=True)
    allergies = Column(Text, nullable=True)
    current_medications = Column(Text, nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by_user = relationship("User", back_populates="patients")
    medical_reports = relationship(
        "MedicalReport", back_populates="patient", cascade="all, delete-orphan"
    )
    ai_summaries = relationship(
        "AISummary", back_populates="patient", cascade="all, delete-orphan"
    )
    diagnoses = relationship(
        "Diagnosis", back_populates="patient", cascade="all, delete-orphan"
    )
    discharge_reports = relationship(
        "DischargeReport", back_populates="patient", cascade="all, delete-orphan"
    )
