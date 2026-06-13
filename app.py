import os
from datetime import date
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

load_dotenv()

from routes import patients, appointments, ai_features, consultations, reminders, analytics, reports
from routes import auth, patient_portal
from services.storage_service import read_json
from services.auth_service import setup_default_users, get_user_by_id

app = FastAPI(title="GramCare", description="Smart Telemedicine Platform for Rural Communities", version="1.0.0")

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "gramcare-secret-2025-rural"))

for d in ["data", "uploads", "prescriptions", "static/css", "static/js", "static/translations"]:
    os.makedirs(d, exist_ok=True)

app.mount("/static",        StaticFiles(directory="static"),        name="static")
app.mount("/prescriptions", StaticFiles(directory="prescriptions"), name="prescriptions")
app.mount("/uploads",       StaticFiles(directory="uploads"),       name="uploads")

templates = Jinja2Templates(directory="templates")

app.include_router(auth.router,           prefix="/auth",          tags=["Auth"])
app.include_router(patient_portal.router, prefix="/portal",        tags=["Patient Portal"])
app.include_router(patients.router,       prefix="/patients",      tags=["Patients"])
app.include_router(appointments.router,   prefix="/appointments",  tags=["Appointments"])
app.include_router(ai_features.router,    prefix="/ai",            tags=["AI Features"])
app.include_router(consultations.router,  prefix="/consultations", tags=["Consultations"])
app.include_router(reminders.router,      prefix="/reminders",     tags=["Reminders"])
app.include_router(analytics.router,      prefix="/analytics",     tags=["Analytics"])
app.include_router(reports.router,        prefix="/reports",       tags=["Reports"])


@app.on_event("startup")
async def on_startup():
    setup_default_users()


@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/auth/login?next=/dashboard")
    if user.get("role") == "patient":
        return RedirectResponse("/portal/")

    uid          = user["id"]
    doctor_data  = get_user_by_id(uid) or {}
    doctor_spec  = doctor_data.get("specialization", "General Physician")

    patients_data      = read_json("data/patients.json")
    appointments_data  = read_json("data/appointments.json")
    consultations_data = read_json("data/consultations.json")
    reminders_data     = read_json("data/reminders.json")

    today = date.today().isoformat()

    def _mine(appts):
        result = []
        for a in appts:
            if a.get("doctor_id"):
                if a["doctor_id"] == uid:
                    result.append(a)
            else:
                spec = a.get("specialty", "General Physician") or "General Physician"
                if doctor_spec == "General Physician" and spec in ("General Physician", ""):
                    result.append(a)
                elif spec == doctor_spec:
                    result.append(a)
        return result

    my_appts        = _mine(appointments_data)
    pending_appts   = sorted([a for a in my_appts if a.get("status") == "pending"],
                             key=lambda x: x.get("created_at", ""))
    upcoming_appts  = sorted([a for a in my_appts
                              if a.get("date", "") >= today and a.get("status") == "scheduled"],
                             key=lambda x: (x.get("date",""), x.get("time","")))
    today_appts     = [a for a in my_appts if a.get("date") == today]

    # Consultations for this doctor
    my_consults = [c for c in consultations_data
                   if c.get("doctor_id") == uid
                   or (not c.get("doctor_id") and c.get("doctor") == doctor_data.get("name",""))]

    # Patients this doctor has seen
    seen_patient_ids = {a.get("patient_id") for a in my_appts}
    seen_patient_ids |= {c.get("patient_id") for c in my_consults}
    my_patient_count = len(seen_patient_ids)

    active_reminders = [r for r in reminders_data if r.get("active", True)]

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "doctor": doctor_data,
        "total_patients":        my_patient_count,
        "today_appointments":    len(today_appts),
        "total_consultations":   len(my_consults),
        "active_reminders":      len(active_reminders),
        "pending_count":         len(pending_appts),
        "recent_patients":       patients_data[-5:][::-1],
        "upcoming_appointments": upcoming_appts[:5],
        "pending_appointments":  pending_appts[:5],
        "recent_consultations":  sorted(my_consults,
                                        key=lambda x: x.get("created_at",""), reverse=True)[:5],
    })


if __name__ == "__main__":
    import uvicorn
    host  = os.getenv("APP_HOST", "0.0.0.0")
    port  = int(os.getenv("APP_PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    uvicorn.run("app:app", host=host, port=port, reload=debug)
