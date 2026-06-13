from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.auth_service import authenticate, register_patient, update_doctor_profile, get_user_by_id, hash_password, verify_password
from services.storage_service import read_json, write_json

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def session_user(request: Request) -> dict | None:
    return request.session.get("user")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = "", next: str = "", role: str = ""):
    user = session_user(request)
    if user:
        return RedirectResponse("/dashboard" if user["role"] == "doctor" else "/portal/")
    return templates.TemplateResponse("login.html", {
        "request": request, "error": error, "next": next, "default_role": role
    })


@router.post("/login")
async def do_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next_url: str = Form("")
):
    user = authenticate(username.strip(), password)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid username or password. Please try again.",
            "next": next_url,
            "default_role": ""
        })
    request.session["user"] = {
        "id":             user["id"],
        "username":       user["username"],
        "role":           user["role"],
        "name":           user["name"],
        "patient_id":     user.get("patient_id", ""),
        "specialization": user.get("specialization", "")
    }
    if next_url:
        return RedirectResponse(next_url, status_code=303)
    return RedirectResponse("/dashboard" if user["role"] == "doctor" else "/portal/", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/auth/login", status_code=303)


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, error: str = ""):
    return templates.TemplateResponse("register.html", {
        "request": request, "error": error, "form": {}
    })


@router.post("/register")
async def do_register(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    address: str = Form(...),
    blood_group: str = Form("Unknown"),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    form = {
        "name": name, "phone": phone, "age": age, "gender": gender,
        "address": address, "blood_group": blood_group
    }
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request, "error": "Passwords do not match.", "form": form
        })
    if len(password) < 6:
        return templates.TemplateResponse("register.html", {
            "request": request, "error": "Password must be at least 6 characters.", "form": form
        })
    try:
        patient, user = register_patient(name, phone, age, gender, address, blood_group, password)
        request.session["user"] = {
            "id": user["id"], "username": user["username"],
            "role": "patient", "name": user["name"], "patient_id": patient["id"]
        }
        return RedirectResponse("/portal/", status_code=303)
    except ValueError as e:
        return templates.TemplateResponse("register.html", {
            "request": request, "error": str(e), "form": form
        })


# ── Doctor profile ──────────────────────────────────────────────────
@router.get("/doctor-profile", response_class=HTMLResponse)
async def doctor_profile_page(request: Request, success: str = ""):
    user = session_user(request)
    if not user or user["role"] != "doctor":
        return RedirectResponse("/auth/login")
    doctor_data = get_user_by_id(user["id"]) or {}
    patients = read_json("data/patients.json")
    consultations = read_json("data/consultations.json")
    appointments = read_json("data/appointments.json")
    return templates.TemplateResponse("doctor_profile.html", {
        "request": request, "user": user,
        "doctor": doctor_data,
        "success": "Profile updated successfully!" if success else "",
        "total_patients": len(patients),
        "total_consultations": len(consultations),
        "total_appointments": len(appointments)
    })


@router.post("/doctor-profile/update")
async def update_profile(
    request: Request,
    name: str = Form(...),
    specialization: str = Form(""),
    qualifications: str = Form(""),
    experience: str = Form(""),
    phone: str = Form(""),
    email: str = Form(""),
    bio: str = Form(""),
    clinic_name: str = Form(""),
    clinic_address: str = Form(""),
    clinic_phone: str = Form(""),
    languages: str = Form(""),
    available_days: str = Form(""),
    work_start: str = Form(""),
    work_end: str = Form(""),
    new_password: str = Form(""),
    confirm_password: str = Form("")
):
    user = session_user(request)
    if not user or user["role"] != "doctor":
        return RedirectResponse("/auth/login")
    if new_password:
        if new_password != confirm_password:
            doctor_data = get_user_by_id(user["id"]) or {}
            patients = read_json("data/patients.json")
            consultations = read_json("data/consultations.json")
            appointments = read_json("data/appointments.json")
            return templates.TemplateResponse("doctor_profile.html", {
                "request": request, "user": user, "doctor": doctor_data,
                "error": "New passwords do not match.",
                "total_patients": len(patients),
                "total_consultations": len(consultations),
                "total_appointments": len(appointments),
            })
        users = read_json("data/users.json")
        for u in users:
            if u["id"] == user["id"]:
                u["password_hash"] = hash_password(new_password)
                break
        write_json("data/users.json", users)
    update_doctor_profile({
        "name": name, "specialization": specialization,
        "qualifications": qualifications, "experience": experience,
        "phone": phone, "email": email, "bio": bio,
        "clinic_name": clinic_name, "clinic_address": clinic_address,
        "clinic_phone": clinic_phone, "languages": languages,
        "available_days": available_days, "work_start": work_start, "work_end": work_end,
    }, user_id=user["id"])
    request.session["user"]["name"] = name
    if user.get("specialization") is not None:
        request.session["user"]["specialization"] = specialization
    return RedirectResponse("/auth/doctor-profile?success=1", status_code=303)
