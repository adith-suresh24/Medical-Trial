from app.database import SessionLocal, init_db
from app.models.user import User, UserRole
from app.utils.security import get_password_hash
from app.models.diagnosis import DiagnosisDatabase


def seed_admin():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "admin").first()
        if not existing:
            admin = User(
                username="admin",
                email="admin@hospital.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print("Admin user created: admin / admin123")
        else:
            print("Admin user already exists")

        if not db.query(User).filter(User.username == "doctor1").first():
            doctor = User(
                username="doctor1",
                email="doctor1@hospital.com",
                hashed_password=get_password_hash("doctor123"),
                full_name="Dr. Sarah Johnson",
                role=UserRole.DOCTOR,
                is_active=True,
            )
            db.add(doctor)
            db.commit()
            print("Doctor user created: doctor1 / doctor123")

        if not db.query(User).filter(User.username == "staff1").first():
            staff = User(
                username="staff1",
                email="staff1@hospital.com",
                hashed_password=get_password_hash("staff123"),
                full_name="Nurse Mike Wilson",
                role=UserRole.STAFF,
                is_active=True,
            )
            db.add(staff)
            db.commit()
            print("Staff user created: staff1 / staff123")

        sample_conditions = [
            {
                "condition_name": "Common Cold (Upper Respiratory Tract Infection)",
                "symptoms": "runny nose, sneezing, sore throat, cough, mild fever, congestion",
                "severity": "mild",
                "description": "A viral infectious disease of the upper respiratory tract.",
                "recommendations": "Rest, hydration, over-the-counter cold medications, consult doctor if fever persists.",
                "common_treatments": "Antihistamines, decongestants, rest, fluids",
                "icd_code": "J00",
            },
            {
                "condition_name": "Hypertension",
                "symptoms": "headache, shortness of breath, nosebleeds, flushing, dizziness, chest pain",
                "severity": "high",
                "description": "Chronic medical condition with elevated blood pressure in the arteries.",
                "recommendations": "Monitor blood pressure regularly, reduce sodium intake, exercise regularly, medication as prescribed.",
                "common_treatments": "ACE inhibitors, beta-blockers, diuretics, lifestyle changes",
                "icd_code": "I10",
            },
            {
                "condition_name": "Type 2 Diabetes Mellitus",
                "symptoms": "frequent urination, increased thirst, increased hunger, weight loss, fatigue, blurred vision",
                "severity": "high",
                "description": "Metabolic disorder characterized by high blood sugar due to insulin resistance.",
                "recommendations": "Blood sugar monitoring, dietary modifications, regular exercise, medication adherence.",
                "common_treatments": "Metformin, insulin therapy, dietary management, exercise",
                "icd_code": "E11",
            },
            {
                "condition_name": "Acute Bronchitis",
                "symptoms": "cough with mucus, chest discomfort, fatigue, mild fever, shortness of breath, wheezing",
                "severity": "moderate",
                "description": "Inflammation of the bronchial tubes, usually due to viral infection.",
                "recommendations": "Rest, fluids, cough medicine, avoid smoke, humidifier use.",
                "common_treatments": "Cough suppressants, bronchodilators, rest, increased fluid intake",
                "icd_code": "J20",
            },
            {
                "condition_name": "Migraine",
                "symptoms": "severe headache, nausea, vomiting, sensitivity to light and sound, visual disturbances",
                "severity": "moderate",
                "description": "Neurological condition causing intense, debilitating headaches.",
                "recommendations": "Rest in dark quiet room, identify triggers, medication at onset, stress management.",
                "common_treatments": "Triptans, NSAIDs, anti-nausea medications, preventive medications",
                "icd_code": "G43",
            },
            {
                "condition_name": "Pneumonia",
                "symptoms": "high fever, chills, cough with phlegm, difficulty breathing, chest pain, confusion",
                "severity": "critical",
                "description": "Infection inflames air sacs in lungs causing fluid buildup.",
                "recommendations": "Immediate medical attention, antibiotics, hospitalization if severe.",
                "common_treatments": "Antibiotics, antiviral medications, oxygen therapy, hospitalization",
                "icd_code": "J18",
            },
            {
                "condition_name": "Gastroenteritis",
                "symptoms": "diarrhea, vomiting, abdominal pain, nausea, fever, dehydration",
                "severity": "moderate",
                "description": "Inflammation of the stomach and intestines, often from infection.",
                "recommendations": "Hydration, bland diet, rest, electrolyte replacement, consult doctor if severe.",
                "common_treatments": "Oral rehydration, antiemetics, antidiarrheals, rest",
                "icd_code": "K52",
            },
            {
                "condition_name": "Urinary Tract Infection (UTI)",
                "symptoms": "burning sensation during urination, frequent urination, cloudy urine, pelvic pain, fever",
                "severity": "moderate",
                "description": "Infection of the urinary system, commonly affecting the bladder and urethra.",
                "recommendations": "Increase fluid intake, antibiotics as prescribed, avoid irritants, follow-up if symptoms persist.",
                "common_treatments": "Antibiotics, increased water intake, cranberry products, urinary analgesics",
                "icd_code": "N39",
            },
            {
                "condition_name": "Anemia",
                "symptoms": "fatigue, weakness, pale skin, shortness of breath, dizziness, cold hands and feet",
                "severity": "moderate",
                "description": "Condition where blood lacks enough healthy red blood cells to carry oxygen.",
                "recommendations": "Iron supplementation, dietary changes, treat underlying cause, monitor hemoglobin levels.",
                "common_treatments": "Iron supplements, vitamin B12, folic acid, blood transfusion if severe",
                "icd_code": "D64",
            },
            {
                "condition_name": "Asthma",
                "symptoms": "wheezing, shortness of breath, chest tightness, coughing (especially at night)",
                "severity": "high",
                "description": "Chronic respiratory condition with airway inflammation and narrowing.",
                "recommendations": "Avoid triggers, use inhalers as prescribed, monitor peak flow, have action plan.",
                "common_treatments": "Inhaled corticosteroids, bronchodilators, leukotriene modifiers",
                "icd_code": "J45",
            },
        ]

        for condition in sample_conditions:
            existing = (
                db.query(DiagnosisDatabase)
                .filter(DiagnosisDatabase.condition_name == condition["condition_name"])
                .first()
            )
            if not existing:
                db.add(DiagnosisDatabase(**condition))

        db.commit()
        print("Diagnosis database seeded with sample conditions")
        print("\nSeed completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    seed_admin()
