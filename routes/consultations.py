from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, date
from services.storage_service import read_json, write_json, generate_id, get_by_id
from services.auth_service import get_user_by_id

router = APIRouter()
templates = Jinja2Templates(directory="templates")

CONSULT_FILE = "data/consultations.json"


def _doctor_user(request: Request) -> dict | None:
    u = request.session.get("user")
    return u if (u and u.get("role") == "doctor") else None


@router.get("/", response_class=HTMLResponse)
async def consultations_page(request: Request):
    user = _doctor_user(request)
    if not user:
        return RedirectResponse("/auth/login")

    doctor_data = get_user_by_id(user["id"]) or {}
    uid = user["id"]

    all_consultations = read_json(CONSULT_FILE)
    # Show only this doctor's consultations
    consultations = [c for c in all_consultations
                     if c.get("doctor_id") == uid
                     or (not c.get("doctor_id") and c.get("doctor") == doctor_data.get("name", ""))]
    consultations_sorted = sorted(consultations, key=lambda x: x.get("created_at", ""), reverse=True)

    patients = read_json("data/patients.json")
    # Only scheduled appointments for this doctor (to link consultations to appointments)
    appointments = [a for a in read_json("data/appointments.json")
                    if a.get("doctor_id") == uid and a.get("status") == "scheduled"]

    return templates.TemplateResponse("consultation.html", {
        "request": request,
        "user": user,
        "doctor": doctor_data,
        "consultations": consultations_sorted,
        "patients": patients,
        "appointments": appointments,
    })


@router.post("/add")
async def add_consultation(
    request: Request,
    patient_id: str = Form(...),
    appointment_id: str = Form(""),
    symptoms: str = Form(...),
    diagnosis: str = Form(...),
    notes: str = Form(...),
    medicines: str = Form(""),
    follow_up_date: str = Form(""),
    recommended_tests: str = Form(""),
):
    user = _doctor_user(request)
    if not user:
        return RedirectResponse("/auth/login")

    doctor_data = get_user_by_id(user["id"]) or {}
    doctor_name = doctor_data.get("name", user.get("name", "Doctor"))

    consultations = read_json(CONSULT_FILE)
    patients = read_json("data/patients.json")
    patient = next((p for p in patients if p["id"] == patient_id), None)
    med_list = [m.strip() for m in medicines.split(",") if m.strip()]
    test_list = [t.strip() for t in recommended_tests.split(",") if t.strip()]

    new_consult = {
        "id":                    generate_id("C", consultations),
        "patient_id":            patient_id,
        "patient_name":          patient["name"] if patient else "Unknown",
        "doctor_id":             user["id"],
        "doctor":                doctor_name,
        "doctor_specialization": doctor_data.get("specialization", ""),
        "appointment_id":        appointment_id,
        "date":                  date.today().isoformat(),
        "symptoms":              symptoms,
        "diagnosis":             diagnosis,
        "notes":                 notes,
        "medicines":             med_list,
        "recommended_tests":     test_list,
        "follow_up_date":        follow_up_date,
        "status":                "completed",
        "created_at":            datetime.now().isoformat()
    }
    consultations.append(new_consult)
    write_json(CONSULT_FILE, consultations)

    # Mark linked appointment as completed
    if appointment_id:
        appts = read_json("data/appointments.json")
        for a in appts:
            if a.get("id") == appointment_id and a.get("doctor_id") == user["id"]:
                a["status"] = "completed"
                break
        write_json("data/appointments.json", appts)

    # Auto-create medicine reminders for the patient (Issue 7)
    if med_list and patient:
        reminders = read_json("data/reminders.json")
        for med in med_list:
            reminders.append({
                "id":           generate_id("R", reminders),
                "patient_id":   patient_id,
                "patient_name": patient["name"] if patient else "Unknown",
                "medicine":     med,
                "frequency":    "As prescribed",
                "time":         "08:00",
                "duration":     "As directed",
                "notes":        f"Prescribed by {doctor_name} for {diagnosis}",
                "active":       True,
                "consultation_id": new_consult["id"],
                "created_at":   datetime.now().isoformat()
            })
        write_json("data/reminders.json", reminders)

    return RedirectResponse(url="/consultations/", status_code=303)


@router.get("/{consult_id}", response_class=HTMLResponse)
async def consultation_detail(request: Request, consult_id: str):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/auth/login")

    consultations = read_json(CONSULT_FILE)
    consult = get_by_id(consultations, consult_id)
    if not consult:
        raise HTTPException(status_code=404, detail="Consultation not found")

    # Patients can only view their own consultations
    if user.get("role") == "patient":
        pid = user.get("patient_id", "")
        if consult.get("patient_id") != pid:
            raise HTTPException(status_code=403, detail="Access denied")

    patients = read_json("data/patients.json")
    patient = next((p for p in patients if p["id"] == consult["patient_id"]), {})

    patient_history = sorted(
        [c for c in consultations if c.get("patient_id") == consult["patient_id"]],
        key=lambda x: x.get("created_at", ""), reverse=True
    )

    # Use patient-styled template when accessed from patient portal
    template_name = "consultation_detail_patient.html" if user.get("role") == "patient" else "consultation_detail.html"

    return templates.TemplateResponse(template_name, {
        "request": request,
        "user": user,
        "consult": consult,
        "patient": patient,
        "patient_history": patient_history,
        "active_page": "reports",
    })
