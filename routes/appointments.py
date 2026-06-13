from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, date
from services.storage_service import read_json, write_json, generate_id, get_by_id, delete_by_id, update_by_id
from services.auth_service import get_user_by_id

router = APIRouter()
templates = Jinja2Templates(directory="templates")

APPT_FILE     = "data/appointments.json"
PATIENTS_FILE = "data/patients.json"

SPECIALTY_LIST = [
    "General Physician", "Cardiologist", "Gynecologist", "Neurologist",
    "Orthopedic", "Dermatologist", "Pediatrician", "ENT", "Psychiatrist", "Ophthalmologist",
]


def _doctor_user(request: Request) -> dict | None:
    u = request.session.get("user")
    return u if (u and u.get("role") == "doctor") else None


def _filter_for_doctor(appointments: list, uid: str, doctor_specialty: str) -> list:
    result = []
    for a in appointments:
        if a.get("doctor_id"):
            if a["doctor_id"] == uid:
                result.append(a)
        else:
            spec = a.get("specialty", "General Physician") or "General Physician"
            if doctor_specialty == "General Physician" and spec in ("General Physician", ""):
                result.append(a)
            elif spec == doctor_specialty:
                result.append(a)
    return result


def _check_ownership(appt_id: str, uid: str, doctor_specialty: str) -> dict | None:
    appts = read_json(APPT_FILE)
    appt = next((a for a in appts if a.get("id") == appt_id), None)
    if not appt:
        return None
    if appt.get("doctor_id"):
        return appt if appt["doctor_id"] == uid else None
    spec = appt.get("specialty", "General Physician") or "General Physician"
    if doctor_specialty == "General Physician" and spec in ("General Physician", ""):
        return appt
    if spec == doctor_specialty:
        return appt
    return None


@router.get("/", response_class=HTMLResponse)
async def appointments_page(request: Request):
    user = _doctor_user(request)
    if not user:
        return RedirectResponse("/auth/login")

    doctor_data      = get_user_by_id(user["id"]) or {}
    doctor_specialty = doctor_data.get("specialization", "General Physician")
    uid              = user["id"]

    appointments = read_json(APPT_FILE)
    patients     = read_json(PATIENTS_FILE)
    today        = date.today().isoformat()

    mine     = _filter_for_doctor(appointments, uid, doctor_specialty)
    pending  = sorted([a for a in mine if a.get("status") == "pending"],
                      key=lambda x: x.get("created_at", ""))
    upcoming = sorted([a for a in mine
                       if a.get("date", "") >= today and a.get("status") not in ("cancelled", "pending")],
                      key=lambda x: (x.get("date", ""), x.get("time", "")))

    return templates.TemplateResponse("appointments.html", {
        "request":              request,
        "user":                 user,
        "doctor":               doctor_data,
        "appointments":         upcoming,
        "pending_appointments": pending,
        "all_appointments":     mine,
        "patients":             patients,
        "today_count":          len([a for a in mine if a.get("date") == today]),
        "pending_count":        len(pending),
        "today":                today,
        "doctor_specialty":     doctor_specialty,
        "specialty_list":       SPECIALTY_LIST,
    })


@router.post("/book")
async def book_appointment(
    request: Request,
    patient_id: str = Form(...),
    specialty: str = Form("General Physician"),
    date: str = Form(...),
    time: str = Form(...),
    type: str = Form(...),
    symptoms: str = Form(""),
    notes: str = Form("")
):
    user = _doctor_user(request)
    if not user:
        return RedirectResponse("/auth/login")

    doctor_data = get_user_by_id(user["id"]) or {}
    appointments = read_json(APPT_FILE)
    patients     = read_json(PATIENTS_FILE)
    patient      = next((p for p in patients if p["id"] == patient_id), None)

    appointments.append({
        "id":           generate_id("A", appointments),
        "patient_id":   patient_id,
        "patient_name": patient["name"] if patient else "Unknown",
        "doctor_id":    user["id"],
        "doctor_name":  doctor_data.get("name", user.get("name", "")),
        "specialty":    specialty,
        "date":         date,
        "time":         time,
        "type":         type,
        "symptoms":     symptoms,
        "notes":        notes,
        "status":       "scheduled",
        "created_at":   datetime.now().isoformat()
    })
    write_json(APPT_FILE, appointments)
    return RedirectResponse(url="/appointments/", status_code=303)


@router.post("/{appt_id}/approve")
async def approve_appointment(request: Request, appt_id: str,
                              new_time: str = Form(""), new_date: str = Form("")):
    user = _doctor_user(request)
    if not user:
        return RedirectResponse("/auth/login")
    doctor_data = get_user_by_id(user["id"]) or {}
    if not _check_ownership(appt_id, user["id"], doctor_data.get("specialization", "General Physician")):
        raise HTTPException(status_code=403, detail="Not authorised")
    updates = {"status": "scheduled", "updated_at": datetime.now().isoformat()}
    if new_date:
        updates["date"] = new_date
    if new_time:
        updates["time"] = new_time
    update_by_id(APPT_FILE, appt_id, updates)
    return RedirectResponse(url="/appointments/", status_code=303)


@router.post("/{appt_id}/reject")
async def reject_appointment(request: Request, appt_id: str, reason: str = Form("")):
    user = _doctor_user(request)
    if not user:
        return RedirectResponse("/auth/login")
    doctor_data = get_user_by_id(user["id"]) or {}
    if not _check_ownership(appt_id, user["id"], doctor_data.get("specialization", "General Physician")):
        raise HTTPException(status_code=403, detail="Not authorised")
    update_by_id(APPT_FILE, appt_id, {
        "status": "cancelled", "rejection_reason": reason,
        "updated_at": datetime.now().isoformat()
    })
    return RedirectResponse(url="/appointments/", status_code=303)


@router.post("/{appt_id}/complete")
async def complete_appointment(request: Request, appt_id: str):
    user = _doctor_user(request)
    if not user:
        return RedirectResponse("/auth/login")
    doctor_data = get_user_by_id(user["id"]) or {}
    if not _check_ownership(appt_id, user["id"], doctor_data.get("specialization", "General Physician")):
        raise HTTPException(status_code=403, detail="Not authorised")
    update_by_id(APPT_FILE, appt_id, {"status": "completed", "updated_at": datetime.now().isoformat()})
    return RedirectResponse(url="/appointments/", status_code=303)


@router.post("/{appt_id}/cancel")
async def cancel_appointment(request: Request, appt_id: str):
    user = _doctor_user(request)
    if not user:
        return RedirectResponse("/auth/login")
    doctor_data = get_user_by_id(user["id"]) or {}
    if not _check_ownership(appt_id, user["id"], doctor_data.get("specialization", "General Physician")):
        raise HTTPException(status_code=403, detail="Not authorised")
    update_by_id(APPT_FILE, appt_id, {"status": "cancelled", "updated_at": datetime.now().isoformat()})
    return RedirectResponse(url="/appointments/", status_code=303)
