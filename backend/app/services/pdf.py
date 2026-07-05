import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from app.config import settings


def generate_discharge_pdf(report, patient, doctor):
    os.makedirs(settings.PDF_OUTPUT_DIR, exist_ok=True)
    filename = f"discharge_{patient.patient_id}_{report.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(settings.PDF_OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=20,
        spaceAfter=6,
        textColor=colors.HexColor("#1a73e8"),
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=20,
        textColor=colors.HexColor("#666666"),
        alignment=TA_CENTER,
    )
    section_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=16,
        spaceAfter=8,
        textColor=colors.HexColor("#333333"),
        borderWidth=1,
        borderColor=colors.HexColor("#1a73e8"),
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=11,
        spaceAfter=6,
        leading=16,
    )
    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#666666"),
        fontName="Helvetica-Bold",
    )

    elements = []

    # Hospital Header
    elements.append(Paragraph("🏥 Hospital Management System", title_style))
    elements.append(Paragraph("Discharge Summary Report", subtitle_style))
    elements.append(Spacer(1, 10))

    # Patient Information
    elements.append(Paragraph("Patient Information", section_style))
    patient_data = [
        [Paragraph("Name:", label_style), Paragraph(f"{patient.first_name} {patient.last_name}", body_style)],
        [Paragraph("Patient ID:", label_style), Paragraph(patient.patient_id, body_style)],
        [Paragraph("Date of Birth:", label_style), Paragraph(str(patient.date_of_birth), body_style)],
        [Paragraph("Gender:", label_style), Paragraph(patient.gender, body_style)],
        [Paragraph("Blood Group:", label_style), Paragraph(patient.blood_group or "N/A", body_style)],
        [Paragraph("Department:", label_style), Paragraph(patient.department or "N/A", body_style)],
    ]
    t = Table(patient_data, colWidths=[120, 350])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 10))

    # Doctor Information
    elements.append(Paragraph("Attending Physician", section_style))
    doctor_data = [
        [Paragraph("Doctor:", label_style), Paragraph(f"Dr. {doctor.full_name}", body_style)],
        [Paragraph("Discharge Date:", label_style), Paragraph(str(report.discharge_date), body_style)],
    ]
    if report.follow_up_date:
        doctor_data.append([
            Paragraph("Follow-up Date:", label_style),
            Paragraph(str(report.follow_up_date), body_style),
        ])
    t = Table(doctor_data, colWidths=[120, 350])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 10))

    # Clinical Information
    elements.append(Paragraph("Diagnosis", section_style))
    elements.append(Paragraph(report.diagnosis, body_style))

    elements.append(Paragraph("Treatment Summary", section_style))
    elements.append(Paragraph(report.treatment_summary, body_style))

    if report.medications_prescribed:
        elements.append(Paragraph("Medications Prescribed", section_style))
        elements.append(Paragraph(report.medications_prescribed, body_style))

    if report.follow_up_instructions:
        elements.append(Paragraph("Follow-up Instructions", section_style))
        elements.append(Paragraph(report.follow_up_instructions, body_style))

    if report.dietary_recommendations:
        elements.append(Paragraph("Dietary Recommendations", section_style))
        elements.append(Paragraph(report.dietary_recommendations, body_style))

    if report.activity_restrictions:
        elements.append(Paragraph("Activity Restrictions", section_style))
        elements.append(Paragraph(report.activity_restrictions, body_style))

    if report.additional_notes:
        elements.append(Paragraph("Additional Notes", section_style))
        elements.append(Paragraph(report.additional_notes, body_style))

    # AI Summary
    if report.ai_summary:
        elements.append(Paragraph("AI-Assisted Summary", section_style))
        ai_note_style = ParagraphStyle(
            "AINote",
            parent=body_style,
            fontName="Helvetica-Oblique",
            textColor=colors.HexColor("#666666"),
            fontSize=9,
        )
        elements.append(Paragraph(report.ai_summary, body_style))
        elements.append(Paragraph(
            "Note: This AI-assisted summary is for reference only. "
            "The final medical decisions remain the responsibility of the attending physician.",
            ai_note_style,
        ))

    elements.append(Spacer(1, 20))

    # Signature
    sig_style = ParagraphStyle(
        "Signature",
        parent=styles["Normal"],
        fontSize=11,
        spaceBefore=40,
    )
    elements.append(Paragraph("_" * 40, sig_style))
    elements.append(Paragraph(f"Dr. {doctor.full_name}", sig_style))
    elements.append(Paragraph("Attending Physician", sig_style))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", sig_style))

    elements.append(Spacer(1, 30))

    # Footer
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#999999"),
        alignment=TA_CENTER,
    )
    elements.append(Paragraph(
        "Hospital Management System | Secure Local Network | HIPAA Compliant",
        footer_style,
    ))
    elements.append(Paragraph(
        "This document is digitally generated and does not require a physical signature.",
        footer_style,
    ))

    doc.build(elements)
    return filepath
