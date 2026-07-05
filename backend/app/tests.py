"""
Comprehensive test suite for Hospital Management System API.
Run with: python3 -m app.tests
"""

import json
import sys
from datetime import datetime, date
from app.database import SessionLocal, init_db
from app.models.user import User
from app.models.patient import Patient
from app.models.medical_report import MedicalReport
from app.models.diagnosis import DiagnosisDatabase
from app.models.discharge_report import DischargeReport
from app.models.access_log import AccessLog
from app.utils.security import get_password_hash, verify_password, create_access_token, decode_access_token


def run_tests():
    passed = 0
    failed = 0

    def test(name, condition):
        nonlocal passed, failed
        try:
            if condition():
                passed += 1
                print(f"  ✅ {name}")
            else:
                failed += 1
                print(f"  ❌ {name}")
        except Exception as e:
            failed += 1
            print(f"  ❌ {name} - Exception: {e}")

    print("\n" + "=" * 50)
    print("Hospital Management System - Test Suite")
    print("=" * 50)

    # Setup
    init_db()
    db = SessionLocal()

    # Clean test data
    db.query(AccessLog).delete()
    db.query(DischargeReport).delete()
    db.query(MedicalReport).delete()
    db.query(Patient).delete()
    db.query(User).filter(User.username.like("test_%")).delete()
    db.commit()

    print("\n📦 Security Tests")
    print("-" * 30)

    def test_password_hashing():
        hashed = get_password_hash("testpass123")
        return verify_password("testpass123", hashed) and not verify_password("wrong", hashed)

    test("Password hashing with bcrypt", test_password_hashing)

    def test_jwt_token():
        token = create_access_token({"user_id": 1, "role": "admin"})
        payload = decode_access_token(token)
        return payload and payload["user_id"] == 1 and payload["role"] == "admin"

    test("JWT token creation and validation", test_jwt_token)

    def test_jwt_expired():
        from datetime import timedelta
        token = create_access_token({"user_id": 1}, expires_delta=timedelta(seconds=-1))
        return decode_access_token(token) is None

    test("JWT expired token rejection", test_jwt_expired)

    print("\n📦 User Model Tests")
    print("-" * 30)

    def test_create_user():
        user = User(
            username="test_doctor",
            email="test_doctor@test.com",
            hashed_password=get_password_hash("test123"),
            full_name="Test Doctor",
            role="doctor",
        )
        db.add(user)
        db.commit()
        return user.id is not None

    test("Create user", test_create_user)

    def test_user_unique_username():
        try:
            user2 = User(
                username="test_doctor",
                email="test_doctor2@test.com",
                hashed_password="hash",
                full_name="Test Doctor 2",
                role="staff",
            )
            db.add(user2)
            db.commit()
            return False
        except Exception:
            db.rollback()
            return True

    test("Unique username constraint", test_user_unique_username)

    print("\n📦 Patient Model Tests")
    print("-" * 30)

    def test_create_patient():
        patient = Patient(
            patient_id="TEST001",
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 1, 15),
            gender="male",
            created_by=1,
        )
        db.add(patient)
        db.commit()
        return patient.id is not None and patient.status == "active"

    test("Create patient", test_create_patient)

    def test_patient_unique_id():
        try:
            p2 = Patient(
                patient_id="TEST001",
                first_name="Jane",
                last_name="Doe",
                date_of_birth=date(1995, 5, 20),
                gender="female",
                created_by=1,
            )
            db.add(p2)
            db.commit()
            return False
        except Exception:
            db.rollback()
            return True

    test("Unique patient ID constraint", test_patient_unique_id)

    def test_update_patient():
        patient = db.query(Patient).filter(Patient.patient_id == "TEST001").first()
        patient.department = "Cardiology"
        patient.ward_number = "W-101"
        db.commit()
        db.refresh(patient)
        return patient.department == "Cardiology"

    test("Update patient", test_update_patient)

    print("\n📦 Medical Report Tests")
    print("-" * 30)

    def test_create_report():
        doctor = db.query(User).filter(User.username == "test_doctor").first()
        patient = db.query(Patient).filter(Patient.patient_id == "TEST001").first()
        report = MedicalReport(
            patient_id=patient.id,
            doctor_id=doctor.id,
            symptoms="fever, cough, headache",
            observations="Patient appears fatigued",
            doctor_notes="Prescribed antibiotics",
        )
        db.add(report)
        db.commit()
        return report.id is not None

    test("Create medical report", test_create_report)

    print("\n📦 Diagnosis Database Tests")
    print("-" * 30)

    def test_diagnosis_match():
        conditions = db.query(DiagnosisDatabase).all()
        return len(conditions) >= 10

    test("Diagnosis database seeded with 10+ conditions", test_diagnosis_match)

    print("\n📦 Discharge Report Tests")
    print("-" * 30)

    def test_create_discharge():
        patient = db.query(Patient).filter(Patient.patient_id == "TEST001").first()
        doctor = db.query(User).filter(User.username == "test_doctor").first()
        report = DischargeReport(
            patient_id=patient.id,
            doctor_id=doctor.id,
            diagnosis="Recovered from infection",
            treatment_summary="Completed antibiotic course",
            discharge_date=date.today(),
        )
        db.add(report)
        db.commit()
        return report.id is not None

    test("Create discharge report", test_create_discharge)

    print("\n📦 Access Log Tests")
    print("-" * 30)

    def test_create_log():
        log = AccessLog(
            user_id=1,
            username="admin",
            action="TEST_ACTION",
            resource="test",
            details="Test log entry",
            status="success",
        )
        db.add(log)
        db.commit()
        return log.id is not None

    test("Create access log", test_create_log)

    # Cleanup test data
    db.query(AccessLog).filter(AccessLog.action == "TEST_ACTION").delete()
    db.query(DischargeReport).delete()
    db.query(MedicalReport).delete()
    db.query(Patient).filter(Patient.patient_id == "TEST001").delete()
    db.query(User).filter(User.username.like("test_%")).delete()
    db.commit()
    db.close()

    print("\n" + "=" * 50)
    total = passed + failed
    print(f"Results: {passed}/{total} passed, {failed}/{total} failed")
    print("=" * 50 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
