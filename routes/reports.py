from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from services.storage_service import read_json, get_by_id
from services.report_service import generate_prescription_pdf, generate_health_report_pdf
from services.gemini_service import analyze_symptoms
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def reports_page(request: Request):
    user = request.session.get("user")
    if not user or user.get("role") != "doctor":
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/auth/login?next=/reports/")
    from services.auth_service import get_user_by_id
    doctor_data = get_user_by_id(user["id"]) or {}
    patients = read_json("data/patients.json")
    consultations = read_json("data/consultations.json")
    pdfs = []
    if os.path.exists("prescriptions"):
        pdfs = [f for f in os.listdir("prescriptions") if f.endswith(".pdf")]
        pdfs.sort(reverse=True)
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "user": user,
        "doctor": doctor_data,
        "patients": patients,
        "consultations": consultations,
        "pdfs": pdfs[:20]
    })


@router.post("/prescription")
async def generate_prescription(
    patient_id: str = Form(...),
    doctor: str = Form(...),
    diagnosis: str = Form(...),
    medicines: str = Form(...),
    instructions: str = Form(""),
    consultation_id: str = Form("MANUAL")
):
    patients = read_json("data/patients.json")
    patient = next((p for p in patients if p["id"] == patient_id), None)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    med_list = [m.strip() for m in medicines.split(",") if m.strip()]
    filepath = generate_prescription_pdf(patient, doctor, diagnosis, med_list, instructions, consultation_id)
    filename = os.path.basename(filepath)
    return FileResponse(filepath, media_type="application/pdf", filename=filename)


@router.post("/health-report")
async def generate_health_report_route(
    patient_id: str = Form(...),
    symptoms: str = Form(...),
    doctor: str = Form("AI Assistant")
):
    patients = read_json("data/patients.json")
    patient = next((p for p in patients if p["id"] == patient_id), None)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    ai_result = analyze_symptoms(symptoms, patient.get("age"), patient.get("gender"))
    filepath = generate_health_report_pdf(patient, symptoms, ai_result, doctor)
    filename = os.path.basename(filepath)
    return FileResponse(filepath, media_type="application/pdf", filename=filename)


@router.get("/prescription/{consult_id}")
async def download_prescription_by_consult(request: Request, consult_id: str):
    """Auto-generate prescription PDF directly from a consultation record."""
    from services.storage_service import get_by_id
    consultations = read_json("data/consultations.json")
    consult = get_by_id(consultations, consult_id)
    if not consult:
        raise HTTPException(status_code=404, detail="Consultation not found")
    patients = read_json("data/patients.json")
    patient = next((p for p in patients if p["id"] == consult.get("patient_id")), None)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    medicines = consult.get("medicines", [])
    if not medicines:
        raise HTTPException(status_code=400, detail="No medicines in this consultation")
    doctor = consult.get("doctor", "Doctor")
    diagnosis = consult.get("diagnosis", "")
    notes = consult.get("notes", "")
    filepath = generate_prescription_pdf(patient, doctor, diagnosis, medicines, notes, consult_id)
    filename = os.path.basename(filepath)
    return FileResponse(filepath, media_type="application/pdf", filename=filename)


@router.get("/health-report/{patient_id}")
async def download_health_report_by_patient(request: Request, patient_id: str):
    """Auto-generate AI health report for a patient from their latest consultation."""
    from services.storage_service import get_by_id
    patients = read_json("data/patients.json")
    patient = next((p for p in patients if p["id"] == patient_id), None)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    consultations = sorted(
        [c for c in read_json("data/consultations.json") if c.get("patient_id") == patient_id],
        key=lambda x: x.get("created_at", ""), reverse=True
    )
    if not consultations:
        raise HTTPException(status_code=404, detail="No consultations found for this patient")
    latest = consultations[0]
    symptoms = latest.get("symptoms", "General checkup")
    doctor = latest.get("doctor", "AI Assistant")
    ai_result = analyze_symptoms(symptoms, patient.get("age"), patient.get("gender"))
    filepath = generate_health_report_pdf(patient, symptoms, ai_result, doctor)
    filename = os.path.basename(filepath)
    return FileResponse(filepath, media_type="application/pdf", filename=filename)


@router.get("/download/{filename}")
async def download_pdf(filename: str):
    filepath = f"prescriptions/{filename}"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath, media_type="application/pdf", filename=filename)
