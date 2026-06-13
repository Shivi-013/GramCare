from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from services.storage_service import read_json, write_json, generate_id, delete_by_id, update_by_id

router = APIRouter()
templates = Jinja2Templates(directory="templates")

REMINDERS_FILE = "data/reminders.json"


@router.get("/", response_class=HTMLResponse)
async def reminders_page(request: Request):
    user = request.session.get("user")
    if not user or user.get("role") != "doctor":
        return RedirectResponse("/auth/login?next=/reminders/")
    reminders = read_json(REMINDERS_FILE)
    patients = read_json("data/patients.json")
    active = [r for r in reminders if r.get("active", True)]
    return templates.TemplateResponse("reminders.html", {
        "request": request,
        "user": user,
        "reminders": reminders,
        "active_reminders": active,
        "patients": patients
    })


@router.post("/add")
async def add_reminder(
    patient_id: str = Form(...),
    medicine: str = Form(...),
    frequency: str = Form(...),
    time: str = Form(...),
    duration: str = Form(...),
    notes: str = Form("")
):
    reminders = read_json(REMINDERS_FILE)
    patients = read_json("data/patients.json")
    patient = next((p for p in patients if p["id"] == patient_id), None)
    new_reminder = {
        "id": generate_id("R", reminders),
        "patient_id": patient_id,
        "patient_name": patient["name"] if patient else "Unknown",
        "medicine": medicine,
        "frequency": frequency,
        "time": time,
        "duration": duration,
        "notes": notes,
        "active": True,
        "created_at": datetime.now().isoformat()
    }
    reminders.append(new_reminder)
    write_json(REMINDERS_FILE, reminders)
    return RedirectResponse(url="/reminders/", status_code=303)


@router.post("/{reminder_id}/delete")
async def delete_reminder(reminder_id: str):
    delete_by_id(REMINDERS_FILE, reminder_id)
    return RedirectResponse(url="/reminders/", status_code=303)


@router.post("/{reminder_id}/toggle")
async def toggle_reminder(reminder_id: str):
    reminders = read_json(REMINDERS_FILE)
    reminder = next((r for r in reminders if r["id"] == reminder_id), None)
    if reminder:
        update_by_id(REMINDERS_FILE, reminder_id, {"active": not reminder.get("active", True)})
    return RedirectResponse(url="/reminders/", status_code=303)
