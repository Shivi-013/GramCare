from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, date
from services.storage_service import read_json, write_json, generate_id
from services.auth_service import hash_password, verify_password
import os

EMERGENCY_KW = [
    "chest pain", "heart attack", "stroke", "can't breathe", "difficulty breathing",
    "unconscious", "fainted", "severe bleeding", "choking", "severe chest",
]


def _is_emergency(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in EMERGENCY_KW)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _patient_user(request: Request) -> dict | None:
    u = request.session.get("user")
    return u if (u and u.get("role") == "patient") else None


# ── Dashboard ────────────────────────────────────────────────────────
@router.get("/", response_class=HTMLResponse)
async def portal_home(request: Request):
    user = _patient_user(request)
    if not user:
        return RedirectResponse("/auth/login?next=/portal/")

    pid = user.get("patient_id", "")
    patients = read_json("data/patients.json")
    patient = next((p for p in patients if p.get("id") == pid), {})

    # Use .get() throughout to handle records that may lack these keys
    appts = [a for a in read_json("data/appointments.json")
             if a.get("patient_id") == pid and pid]
    consultations = [c for c in read_json("data/consultations.json")
                     if c.get("patient_id") == pid and pid]
    reminders = [r for r in read_json("data/reminders.json")
                 if r.get("patient_id") == pid and pid and r.get("active")]

    today = date.today().isoformat()
    upcoming = sorted(
        [a for a in appts if a.get("date", "") >= today
         and a.get("status") in ("scheduled", "pending")],
        key=lambda x: x.get("date", "")
    )
    latest_consult = sorted(consultations, key=lambda x: x.get("created_at", ""), reverse=True)

    return templates.TemplateResponse("patient_dashboard.html", {
        "request": request, "user": user, "patient": patient,
        "active_page": "home",
        "upcoming_appointments": upcoming[:3],
        "upcoming_count": len(upcoming),
        "pending_count": sum(1 for a in appts if a.get("status") == "pending"),
        "total_consultations": len(consultations),
        "active_reminders": len(reminders),
        "latest_reminder": reminders[0] if reminders else None,
        "latest_consultation": latest_consult[0] if latest_consult else None,
    })


# ── Appointments ─────────────────────────────────────────────────────
@router.get("/appointments", response_class=HTMLResponse)
async def portal_appointments(request: Request):
    user = _patient_user(request)
    if not user:
        return RedirectResponse("/auth/login?next=/portal/appointments")
    pid = user.get("patient_id", "")
    appts = sorted(
        [a for a in read_json("data/appointments.json")
         if a.get("patient_id") == pid and pid],
        key=lambda x: x.get("date", ""), reverse=True
    )
    doctors = [
        {k: u.get(k, "") for k in
         ("id", "name", "specialization", "qualifications", "experience", "bio")}
        for u in read_json("data/users.json")
        if u.get("role") == "doctor"
    ]
    return templates.TemplateResponse("patient_appointments.html", {
        "request": request, "user": user,
        "active_page": "appointments",
        "appointments": appts,
        "doctors": doctors,
        "today": date.today().isoformat(),
    })


@router.post("/appointments/book")
async def portal_book_appt(
    request: Request,
    specialty: str = Form("General Physician"),
    doctor_id: str = Form(""),
    doctor_name: str = Form(""),
    date: str = Form(...),
    time: str = Form(...),
    type: str = Form(...),
    symptoms: str = Form(""),
    duration: str = Form(""),
    notes: str = Form("")
):
    user = _patient_user(request)
    if not user:
        return RedirectResponse("/auth/login")
    appts = read_json("data/appointments.json")
    full_symptoms = symptoms
    if duration:
        full_symptoms = f"{symptoms} (Duration: {duration})" if symptoms else f"Duration: {duration}"
    appts.append({
        "id":           generate_id("A", appts),
        "patient_id":   user.get("patient_id", ""),
        "patient_name": user.get("name", ""),
        "specialty":    specialty,
        "doctor_id":    doctor_id,
        "doctor_name":  doctor_name,
        "date":         date,
        "time":         time,
        "type":         type,
        "status":       "pending",
        "symptoms":     full_symptoms,
        "notes":        notes,
        "created_at":   datetime.now().isoformat()
    })
    write_json("data/appointments.json", appts)
    return RedirectResponse("/portal/appointments", status_code=303)


@router.post("/appointments/{appt_id}/cancel")
async def portal_cancel_appt(request: Request, appt_id: str):
    user = _patient_user(request)
    if not user:
        return RedirectResponse("/auth/login")
    pid = user.get("patient_id", "")
    appts = read_json("data/appointments.json")
    for a in appts:
        if a.get("id") == appt_id and a.get("patient_id") == pid:
            if a.get("status") in ("pending", "scheduled"):
                a["status"] = "cancelled"
            break
    write_json("data/appointments.json", appts)
    return RedirectResponse("/portal/appointments", status_code=303)


# ── Medicines ─────────────────────────────────────────────────────────
@router.get("/medicines", response_class=HTMLResponse)
async def portal_medicines(request: Request):
    user = _patient_user(request)
    if not user:
        return RedirectResponse("/auth/login?next=/portal/medicines")
    pid = user.get("patient_id", "")
    consultations = sorted(
        [c for c in read_json("data/consultations.json")
         if c.get("patient_id") == pid and pid],
        key=lambda x: x.get("created_at", ""), reverse=True
    )
    return templates.TemplateResponse("patient_medicines.html", {
        "request": request, "user": user,
        "active_page": "medicines",
        "consultations": consultations
    })


# ── Reminders ─────────────────────────────────────────────────────────
@router.get("/reminders", response_class=HTMLResponse)
async def portal_reminders(request: Request):
    user = _patient_user(request)
    if not user:
        return RedirectResponse("/auth/login?next=/portal/reminders")
    pid = user.get("patient_id", "")
    reminders = [r for r in read_json("data/reminders.json")
                 if r.get("patient_id") == pid and pid]
    return templates.TemplateResponse("patient_reminders.html", {
        "request": request, "user": user,
        "active_page": "reminders",
        "reminders": reminders,
    })


# ── Reports ───────────────────────────────────────────────────────────
@router.get("/reports", response_class=HTMLResponse)
async def portal_reports(request: Request):
    user = _patient_user(request)
    if not user:
        return RedirectResponse("/auth/login?next=/portal/reports")
    pid = user.get("patient_id", "")
    patients_list = read_json("data/patients.json")
    patient = next((p for p in patients_list if p.get("id") == pid), {})
    consultations = sorted(
        [c for c in read_json("data/consultations.json")
         if c.get("patient_id") == pid and pid],
        key=lambda x: x.get("created_at", ""), reverse=True
    )
    pdfs = sorted([f for f in os.listdir("prescriptions") if f.endswith(".pdf")], reverse=True)[:20] \
        if os.path.exists("prescriptions") else []
    return templates.TemplateResponse("patient_reports.html", {
        "request": request, "user": user, "patient": patient,
        "active_page": "reports",
        "consultations": consultations, "pdfs": pdfs
    })


@router.get("/reports/download/{filename}")
async def portal_download(request: Request, filename: str):
    user = _patient_user(request)
    if not user:
        return RedirectResponse("/auth/login")
    filepath = f"prescriptions/{filename}"
    if not os.path.exists(filepath):
        return RedirectResponse("/portal/reports")
    return FileResponse(filepath, media_type="application/pdf", filename=filename)


# ── Profile ───────────────────────────────────────────────────────────
@router.get("/profile", response_class=HTMLResponse)
async def portal_profile(request: Request, success: str = ""):
    user = _patient_user(request)
    if not user:
        return RedirectResponse("/auth/login?next=/portal/profile")
    pid = user.get("patient_id", "")
    patients_list = read_json("data/patients.json")
    patient = next((p for p in patients_list if p.get("id") == pid), {})
    return templates.TemplateResponse("patient_profile.html", {
        "request": request, "user": user, "patient": patient,
        "active_page": "profile",
        "success": "Password updated successfully!" if success else "",
        "error": ""
    })


@router.post("/profile/change-password")
async def portal_change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    user = _patient_user(request)
    if not user:
        return RedirectResponse("/auth/login")
    pid = user.get("patient_id", "")
    patients_list = read_json("data/patients.json")
    patient = next((p for p in patients_list if p.get("id") == pid), {})

    if new_password != confirm_password:
        return templates.TemplateResponse("patient_profile.html", {
            "request": request, "user": user, "patient": patient,
            "active_page": "profile", "error": "New passwords do not match.", "success": ""
        })

    users = read_json("data/users.json")
    for u in users:
        if u.get("id") == user.get("id"):
            if not verify_password(current_password, u.get("password_hash", "")):
                return templates.TemplateResponse("patient_profile.html", {
                    "request": request, "user": user, "patient": patient,
                    "active_page": "profile", "error": "Current password is incorrect.", "success": ""
                })
            u["password_hash"] = hash_password(new_password)
            break
    write_json("data/users.json", users)
    return RedirectResponse("/portal/profile?success=1", status_code=303)


# ── Timeline ─────────────────────────────────────────────────────────
@router.get("/timeline", response_class=HTMLResponse)
async def portal_timeline(request: Request):
    user = _patient_user(request)
    if not user:
        return RedirectResponse("/auth/login?next=/portal/timeline")
    pid = user.get("patient_id", "")

    appts = sorted(
        [a for a in read_json("data/appointments.json") if a.get("patient_id") == pid and pid],
        key=lambda x: x.get("date", ""), reverse=True
    )
    consultations = sorted(
        [c for c in read_json("data/consultations.json") if c.get("patient_id") == pid and pid],
        key=lambda x: x.get("date", ""), reverse=True
    )

    # Merge into a single timeline sorted by date descending
    events = []
    for a in appts:
        events.append({
            "date": a.get("date", ""),
            "type": "appointment",
            "title": f"Appointment – {a.get('specialty', 'General Physician')}",
            "doctor": a.get("doctor_name", ""),
            "specialty": a.get("specialty", ""),
            "status": a.get("status", ""),
            "symptoms": a.get("symptoms", ""),
            "notes": a.get("notes", ""),
            "id": a.get("id", ""),
        })
    for c in consultations:
        events.append({
            "date": c.get("date", ""),
            "type": "consultation",
            "title": f"Consultation – {c.get('doctor_specialization', c.get('specialty', ''))}",
            "doctor": c.get("doctor", ""),
            "specialty": c.get("doctor_specialization", ""),
            "status": "completed",
            "diagnosis": c.get("diagnosis", ""),
            "medicines": c.get("medicines", []),
            "follow_up": c.get("follow_up_date", ""),
            "notes": c.get("notes", ""),
            "id": c.get("id", ""),
        })

    events.sort(key=lambda x: x.get("date", ""), reverse=True)

    return templates.TemplateResponse("patient_timeline.html", {
        "request": request, "user": user,
        "active_page": "timeline",
        "events": events,
        "total_visits": len(appts),
        "total_consults": len(consultations),
    })


# ── AI Symptom Checker ────────────────────────────────────────────────
@router.get("/symptoms", response_class=HTMLResponse)
async def portal_symptoms(request: Request):
    user = _patient_user(request)
    if not user:
        return RedirectResponse("/auth/login?next=/portal/symptoms")
    pid = user.get("patient_id", "")
    patients_list = read_json("data/patients.json")
    patient = next((p for p in patients_list if p.get("id") == pid), {})
    return templates.TemplateResponse("patient_symptoms.html", {
        "request": request, "user": user, "patient": patient,
        "active_page": "symptoms", "result": None, "symptoms_input": "",
        "suggested_doctors": [], "is_emergency": False,
    })


@router.post("/symptoms/check", response_class=HTMLResponse)
async def portal_symptoms_check(request: Request, symptoms: str = Form(...)):
    user = _patient_user(request)
    if not user:
        return RedirectResponse("/auth/login")
    pid = user.get("patient_id", "")
    patients_list = read_json("data/patients.json")
    patient = next((p for p in patients_list if p.get("id") == pid), {})

    from services.gemini_service import suggest_doctor_from_symptoms
    is_emergency = _is_emergency(symptoms)
    result = suggest_doctor_from_symptoms(
        symptoms,
        patient.get("age"),
        patient.get("gender")
    )
    if is_emergency:
        result["emergency"] = True
        result["urgency"] = "Immediate"
        result["urgency_color"] = "red"

    suggested_spec = result.get("suggested_specialty", "General Physician")
    all_users = read_json("data/users.json")
    suggested_doctors = [
        {k: u.get(k, "") for k in
         ("id", "name", "specialization", "qualifications", "experience", "bio")}
        for u in all_users
        if u.get("role") == "doctor" and u.get("specialization") == suggested_spec
    ]

    return templates.TemplateResponse("patient_symptoms.html", {
        "request": request, "user": user, "patient": patient,
        "active_page": "symptoms",
        "result": result,
        "symptoms_input": symptoms,
        "suggested_doctors": suggested_doctors,
        "is_emergency": is_emergency,
    })
