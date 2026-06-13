from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.gemini_service import analyze_symptoms, triage_patient
from services.storage_service import read_json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "stroke", "difficulty breathing",
    "breathlessness", "unconscious", "fainted", "severe bleeding",
    "paralysis", "can't breathe", "choking", "severe chest"
]


def check_emergency(symptoms: str) -> bool:
    s = symptoms.lower()
    return any(kw in s for kw in EMERGENCY_KEYWORDS)


def _doctor_user(request: Request) -> dict | None:
    u = request.session.get("user")
    return u if (u and u.get("role") == "doctor") else None


@router.get("/symptoms", response_class=HTMLResponse)
async def symptom_page(request: Request):
    user = _doctor_user(request)
    if not user:
        return RedirectResponse("/auth/login?next=/ai/symptoms")
    patients = read_json("data/patients.json")
    return templates.TemplateResponse("ai_symptoms.html", {"request": request, "user": user, "patients": patients})


@router.post("/symptoms/check")
async def check_symptoms(
    request: Request,
    symptoms: str = Form(...),
    patient_id: str = Form(""),
    age: int = Form(None),
    gender: str = Form("")
):
    user = _doctor_user(request)
    if not user:
        return RedirectResponse("/auth/login")
    patients = read_json("data/patients.json")
    patient = next((p for p in patients if p["id"] == patient_id), None) if patient_id else None
    p_age = patient["age"] if patient else age
    p_gender = patient["gender"] if patient else gender

    is_emergency = check_emergency(symptoms)
    result = analyze_symptoms(symptoms, p_age, p_gender)
    if is_emergency:
        result["emergency"] = True
        result["severity"] = "Emergency"

    return templates.TemplateResponse("ai_symptoms.html", {
        "request": request,
        "user": user,
        "patients": patients,
        "result": result,
        "symptoms": symptoms,
        "patient": patient,
        "is_emergency": is_emergency
    })


@router.get("/triage", response_class=HTMLResponse)
async def triage_page(request: Request):
    user = _doctor_user(request)
    if not user:
        return RedirectResponse("/auth/login?next=/ai/triage")
    patients = read_json("data/patients.json")
    return templates.TemplateResponse("ai_triage.html", {"request": request, "user": user, "patients": patients})


@router.post("/triage/assess")
async def assess_triage(
    request: Request,
    age: int = Form(...),
    symptoms: str = Form(...),
    duration: str = Form(...),
    existing_conditions: str = Form(""),
    patient_id: str = Form("")
):
    user = _doctor_user(request)
    if not user:
        return RedirectResponse("/auth/login")
    patients = read_json("data/patients.json")
    patient = next((p for p in patients if p["id"] == patient_id), None) if patient_id else None
    if patient:
        age = patient["age"]

    is_emergency = check_emergency(symptoms)
    result = triage_patient(age, symptoms, duration, existing_conditions)
    if is_emergency:
        result["emergency"] = True
        result["priority"] = "Emergency"
        result["priority_score"] = 10

    return templates.TemplateResponse("ai_triage.html", {
        "request": request,
        "user": user,
        "patients": patients,
        "result": result,
        "symptoms": symptoms,
        "patient": patient,
        "is_emergency": is_emergency,
        "age": age,
        "duration": duration
    })


@router.post("/symptoms/api")
async def api_check_symptoms(request: Request):
    if not _doctor_user(request):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    body = await request.json()
    symptoms = body.get("symptoms", "")
    age = body.get("age")
    gender = body.get("gender", "")
    is_emergency = check_emergency(symptoms)
    result = analyze_symptoms(symptoms, age, gender)
    if is_emergency:
        result["emergency"] = True
    return JSONResponse(result)
