import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

GREEN = colors.HexColor("#22C55E")
BLUE = colors.HexColor("#3B82F6")
DARK = colors.HexColor("#1F2937")
GRAY = colors.HexColor("#6B7280")
LIGHT = colors.HexColor("#F0FDF4")
RED = colors.HexColor("#EF4444")


def _base_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("RCTitle", parent=styles["Title"], fontSize=22, textColor=GREEN,
                               spaceAfter=4, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle("RCSubtitle", parent=styles["Normal"], fontSize=10, textColor=GRAY,
                               spaceAfter=2))
    styles.add(ParagraphStyle("RCSectionHead", parent=styles["Heading2"], fontSize=13,
                               textColor=BLUE, spaceBefore=12, spaceAfter=6, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle("RCBody", parent=styles["Normal"], fontSize=10, textColor=DARK,
                               spaceAfter=4, leading=16))
    styles.add(ParagraphStyle("RCSmall", parent=styles["Normal"], fontSize=8, textColor=GRAY))
    styles.add(ParagraphStyle("RCCenter", parent=styles["Normal"], fontSize=10, alignment=TA_CENTER))
    styles.add(ParagraphStyle("RCBold", parent=styles["Normal"], fontSize=10, fontName="Helvetica-Bold"))
    return styles


def _header_block(styles, title: str, subtitle: str) -> list:
    elements = []
    elements.append(Paragraph("GramCare", styles["RCTitle"]))
    elements.append(Paragraph("ग्रामकेयर – Smart Telemedicine for Rural Communities", styles["RCSubtitle"]))
    elements.append(HRFlowable(width="100%", thickness=2, color=GREEN, spaceAfter=8))
    elements.append(Paragraph(title, styles["RCSectionHead"]))
    elements.append(Paragraph(subtitle, styles["RCSmall"]))
    elements.append(Spacer(1, 12))
    return elements


def generate_prescription_pdf(patient: dict, doctor: str, diagnosis: str,
                               medicines: list, instructions: str, consultation_id: str) -> str:
    os.makedirs("prescriptions", exist_ok=True)
    filename = f"prescriptions/prescription_{consultation_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = _base_styles()
    story = []

    story.extend(_header_block(styles, "Medical Prescription",
                                f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}"))

    # Patient & Doctor info table
    info_data = [
        ["Patient Name", patient.get("name", "N/A"), "Doctor", doctor],
        ["Age / Gender", f"{patient.get('age', 'N/A')} / {patient.get('gender', 'N/A')}",
         "Date", datetime.now().strftime("%d-%m-%Y")],
        ["Phone", patient.get("phone", "N/A"), "Blood Group", patient.get("blood_group", "N/A")],
        ["Address", patient.get("address", "N/A"), "", ""],
    ]
    info_table = Table(info_data, colWidths=[3.5*cm, 7*cm, 3.5*cm, 4.5*cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
        ("BACKGROUND", (2, 0), (2, -1), LIGHT),
        ("TEXTCOLOR", (0, 0), (-1, -1), DARK),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1FAE5")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    # Diagnosis
    story.append(Paragraph("Diagnosis", styles["RCSectionHead"]))
    story.append(Paragraph(diagnosis, styles["RCBody"]))
    story.append(Spacer(1, 8))

    # Medicines
    story.append(Paragraph("Prescribed Medicines", styles["RCSectionHead"]))
    med_data = [["#", "Medicine / Dosage", "Instructions"]]
    for i, med in enumerate(medicines, 1):
        med_data.append([str(i), med, "As directed"])
    med_table = Table(med_data, colWidths=[1*cm, 10*cm, 7*cm])
    med_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1FAE5")),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(med_table)
    story.append(Spacer(1, 12))

    # Instructions
    if instructions:
        story.append(Paragraph("Special Instructions", styles["RCSectionHead"]))
        story.append(Paragraph(instructions, styles["RCBody"]))
        story.append(Spacer(1, 12))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=GREEN, spaceAfter=8))
    story.append(Paragraph(
        "This prescription is generated by GramCare. Always consult a licensed physician.",
        styles["RCSmall"]
    ))
    story.append(Paragraph(
        f"Doctor's Signature: {doctor}                    Date: {datetime.now().strftime('%d-%m-%Y')}",
        styles["RCBody"]
    ))

    doc.build(story)
    return filename


def generate_health_report_pdf(patient: dict, symptoms: str, ai_result: dict,
                                doctor: str = "AI Assistant") -> str:
    os.makedirs("prescriptions", exist_ok=True)
    filename = f"prescriptions/health_report_{patient.get('id', 'TEMP')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = _base_styles()
    story = []

    story.extend(_header_block(styles, "AI Health Analysis Report",
                                f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}"))

    # Patient info
    info_data = [
        ["Patient Name", patient.get("name", "N/A"), "Age", str(patient.get("age", "N/A"))],
        ["Gender", patient.get("gender", "N/A"), "Phone", patient.get("phone", "N/A")],
        ["Blood Group", patient.get("blood_group", "N/A"), "Address", patient.get("address", "N/A")],
    ]
    info_table = Table(info_data, colWidths=[3.5*cm, 7*cm, 3.5*cm, 4.5*cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
        ("BACKGROUND", (2, 0), (2, -1), LIGHT),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1FAE5")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    # Symptoms
    story.append(Paragraph("Reported Symptoms", styles["RCSectionHead"]))
    story.append(Paragraph(symptoms, styles["RCBody"]))
    story.append(Spacer(1, 8))

    # Severity badge
    severity = ai_result.get("severity", "Medium")
    sev_color = {"Low": colors.HexColor("#22C55E"), "Medium": colors.HexColor("#F59E0B"),
                 "High": colors.HexColor("#EF4444"), "Emergency": colors.HexColor("#7C3AED")}.get(severity, GRAY)
    story.append(Paragraph("Severity Assessment", styles["RCSectionHead"]))
    sev_table = Table([[f"  {severity}  ", ai_result.get("severity_reason", "")]], colWidths=[4*cm, 14.5*cm])
    sev_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), sev_color),
        ("TEXTCOLOR", (0, 0), (0, 0), colors.white),
        ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(sev_table)
    story.append(Spacer(1, 8))

    # Possible conditions
    story.append(Paragraph("Possible Conditions", styles["RCSectionHead"]))
    for cond in ai_result.get("possible_conditions", []):
        story.append(Paragraph(f"• {cond}", styles["RCBody"]))
    story.append(Spacer(1, 8))

    # Recommendations
    story.append(Paragraph("Recommendations", styles["RCSectionHead"]))
    for rec in ai_result.get("recommendations", []):
        story.append(Paragraph(f"✓ {rec}", styles["RCBody"]))
    story.append(Spacer(1, 8))

    # Home remedies
    if ai_result.get("home_remedies"):
        story.append(Paragraph("Home Remedies", styles["RCSectionHead"]))
        for rem in ai_result["home_remedies"]:
            story.append(Paragraph(f"• {rem}", styles["RCBody"]))
        story.append(Spacer(1, 8))

    # When to seek care
    story.append(Paragraph("When to Seek Care", styles["RCSectionHead"]))
    story.append(Paragraph(ai_result.get("when_to_seek_care", "As needed"), styles["RCBold"]))
    story.append(Spacer(1, 12))

    # Disclaimer
    story.append(HRFlowable(width="100%", thickness=1, color=GREEN, spaceAfter=8))
    story.append(Paragraph(
        "DISCLAIMER: This is an AI-generated health analysis report and should NOT replace professional medical advice. "
        "Always consult a licensed doctor for proper diagnosis and treatment.",
        styles["RCSmall"]
    ))

    doc.build(story)
    return filename
