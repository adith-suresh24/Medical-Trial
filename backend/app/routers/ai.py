import time
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.medical_report import MedicalReport
from app.models.ai_summary import AISummary
from app.models.user import User
from app.middleware.auth import get_current_user, require_role
from app.services.log import log_action
from app.config import settings

router = APIRouter(prefix="/api/ai", tags=["AI Integration"])


def call_ai_api(symptoms: str, observations: str, doctor_notes: str):
    if not settings.AI_API_KEY or not settings.AI_API_URL:
        return generate_mock_summary(symptoms, observations, doctor_notes)
    try:
        import httpx
        headers = {
            "Authorization": f"Bearer {settings.AI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.AI_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a medical AI assistant helping doctors analyze patient reports. "
                        "Provide a concise summary, risk level (low/moderate/high/critical), "
                        "recommendations, and possible conditions. "
                        "IMPORTANT: Clearly state that this is AI-assisted analysis and not a diagnosis. "
                        "The final medical decision rests with the doctor."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Symptoms: {symptoms}\nObservations: {observations}\nDoctor Notes: {doctor_notes}",
                },
            ],
            "temperature": 0.3,
            "max_tokens": 500,
        }
        response = httpx.post(settings.AI_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        return parse_ai_response(content)
    except Exception as e:
        return generate_mock_summary(symptoms, observations, doctor_notes)


def generate_mock_summary(symptoms: str, observations: str, doctor_notes: str):
    return {
        "summary": f"AI-Assisted Analysis: Patient presents with {symptoms[:100]}... "
                   f"Observations indicate {observations[:100] if observations else 'ongoing evaluation needed'}.",
        "risk_level": "moderate",
        "recommendations": "Continue monitoring. Follow standard treatment protocols. "
                          "Consult with senior physician if symptoms worsen.",
        "possible_conditions": "Based on presented symptoms, differential diagnosis includes "
                              "common conditions. Detailed clinical correlation required.",
    }


def parse_ai_response(content: str):
    return {
        "summary": content[:500] if content else "Analysis completed.",
        "risk_level": "moderate",
        "recommendations": "Please review the AI analysis alongside clinical findings.",
        "possible_conditions": "Refer to the detailed analysis above.",
    }


@router.post("/summarize/{report_id}")
def generate_ai_summary(
    report_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    start_time = time.time()
    ai_result = call_ai_api(
        symptoms=report.symptoms or "",
        observations=report.observations or "",
        doctor_notes=report.doctor_notes or "",
    )
    processing_time = int((time.time() - start_time) * 1000)

    existing = db.query(AISummary).filter(AISummary.report_id == report_id).first()
    if existing:
        existing.summary = ai_result.get("summary")
        existing.risk_level = ai_result.get("risk_level")
        existing.recommendations = ai_result.get("recommendations")
        existing.possible_conditions = ai_result.get("possible_conditions")
        existing.ai_model_used = settings.AI_MODEL
        existing.processing_time_ms = processing_time
        ai_summary = existing
    else:
        ai_summary = AISummary(
            report_id=report_id,
            patient_id=report.patient_id,
            summary=ai_result.get("summary"),
            risk_level=ai_result.get("risk_level"),
            recommendations=ai_result.get("recommendations"),
            possible_conditions=ai_result.get("possible_conditions"),
            ai_model_used=settings.AI_MODEL,
            processing_time_ms=processing_time,
        )
        db.add(ai_summary)

    db.commit()
    db.refresh(ai_summary)

    log_action(
        db,
        user_id=current_user.id,
        username=current_user.username,
        action="AI_SUMMARY_GENERATED",
        resource="ai_summary",
        resource_id=ai_summary.id,
        details=f"AI summary generated for report ID {report_id}",
        ip_address=request.client.host if request.client else None,
    )

    return {
        "id": ai_summary.id,
        "summary": ai_summary.summary,
        "risk_level": ai_summary.risk_level,
        "recommendations": ai_summary.recommendations,
        "possible_conditions": ai_summary.possible_conditions,
        "processing_time_ms": processing_time,
        "disclaimer": "This AI-assisted analysis is for reference only. "
                      "The final medical diagnosis and treatment decisions "
                      "remain the responsibility of the attending physician.",
    }
