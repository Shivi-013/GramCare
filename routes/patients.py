from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from services.storage_service import read_json, write_json, generate_id, get_by_id, delete_by_id

router = APIRouter()
templates = Jinja2Templates(directory="templates")

PATIENTS_FILE = "data/patients.json"


@router.get("/", response_class=HTMLResponse)
async def patients_page(request: Request, search: str = ""):
    user = request.session.get("user")
    if not user or user.get("role") != "doctor":
        return RedirectResponse("/auth/login?next=/patients/")
    patients = read_json(PATIENTS_FILE)
    if search:
        q = search.lower()
        patients = [p for p in patients if q in p["name"].lower() or q in p.get("phone", "")]
    return templates.TemplateResponse("patients.html", {
        "request": request,
        "user": user,
        "patients": patients,
        "search": search,
        "total": len(patients)
    })


@router.post("/add")
async def add_patient(
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    blood_group: str = Form("Unknown")
):
    patients = read_json(PATIENTS_FILE)
    new_patient = {
        "id": generate_id("P", patients),
        "name": name,
        "age": age,
        "gender": gender,
        "phone": phone,
        "address": address,
        "blood_group": blood_group,
        "created_at": datetime.now().isoformat()
    }
    patients.append(new_patient)
    write_json(PATIENTS_FILE, patients)
    return RedirectResponse(url="/patients/", status_code=303)


@router.get("/{patient_id}", response_class=HTMLResponse)
async def patient_detail(request: Request, patient_id: str):
    user = request.session.get("user")
    if not user or user.get("role") != "doctor":
        return RedirectResponse("/auth/login")
    patients = read_json(PATIENTS_FILE)
    patient = get_by_id(patients, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    consultations = [c for c in read_json("data/consultations.json") if c["patient_id"] == patient_id]
    appointments = [a for a in read_json("data/appointments.json") if a["patient_id"] == patient_id]
    reminders = [r for r in read_json("data/reminders.json") if r["patient_id"] == patient_id]
    return templates.TemplateResponse("patient_detail.html", {
        "request": request,
        "user": user,
        "patient": patient,
        "consultations": consultations,
        "appointments": appointments,
        "reminders": reminders
    })


@router.post("/{patient_id}/delete")
async def delete_patient(patient_id: str):
    deleted = delete_by_id(PATIENTS_FILE, patient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Patient not found")
    return RedirectResponse(url="/patients/", status_code=303)


@router.get("/api/list", response_class=JSONResponse)
async def api_patients_list():
    return read_json(PATIENTS_FILE)
