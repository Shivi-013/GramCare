from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import date, timedelta
from collections import Counter, defaultdict
from services.storage_service import read_json

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def analytics_page(request: Request):
    user = request.session.get("user")
    if not user or user.get("role") != "doctor":
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/auth/login?next=/analytics/")
    return templates.TemplateResponse("analytics.html", {"request": request, "user": user})


@router.get("/data", response_class=JSONResponse)
async def analytics_data():
    patients = read_json("data/patients.json")
    appointments = read_json("data/appointments.json")
    consultations = read_json("data/consultations.json")

    # Appointments per week (last 7 weeks)
    today = date.today()
    week_labels = []
    week_counts = []
    for i in range(6, -1, -1):
        week_start = today - timedelta(weeks=i, days=today.weekday())
        week_end = week_start + timedelta(days=6)
        label = f"W{7-i}: {week_start.strftime('%d %b')}"
        count = sum(
            1 for a in appointments
            if week_start.isoformat() <= a.get("date", "") <= week_end.isoformat()
        )
        week_labels.append(label)
        week_counts.append(count)

    # Patient age distribution
    age_buckets = {"0-18": 0, "19-35": 0, "36-50": 0, "51-65": 0, "65+": 0}
    for p in patients:
        age = p.get("age", 0)
        if age <= 18: age_buckets["0-18"] += 1
        elif age <= 35: age_buckets["19-35"] += 1
        elif age <= 50: age_buckets["36-50"] += 1
        elif age <= 65: age_buckets["51-65"] += 1
        else: age_buckets["65+"] += 1

    # Disease categories from consultations
    diagnoses = [c.get("diagnosis", "Other") for c in consultations]
    disease_counter = Counter(diagnoses)
    top_diseases = dict(disease_counter.most_common(6))

    # Consultation trend (last 30 days, grouped by week)
    trend_labels = []
    trend_counts = []
    for i in range(3, -1, -1):
        week_start = today - timedelta(weeks=i+1)
        week_end = today - timedelta(weeks=i)
        count = sum(
            1 for c in consultations
            if week_start.isoformat() <= c.get("date", "") < week_end.isoformat()
        )
        trend_labels.append(f"{week_start.strftime('%d %b')}")
        trend_counts.append(count)

    # Gender distribution
    genders = Counter(p.get("gender", "Unknown") for p in patients)

    # Appointment type distribution
    appt_types = Counter(a.get("type", "General") for a in appointments)

    # Medicine frequency
    med_counter: Counter = Counter()
    for c in consultations:
        for med in (c.get("medicines") or []):
            name = med.get("name") if isinstance(med, dict) else str(med)
            if name:
                med_counter[name.strip()] += 1
    top_meds = dict(med_counter.most_common(8))

    # Appointment status breakdown
    reminders = read_json("data/reminders.json")
    pending_count  = sum(1 for a in appointments if a.get("status") == "pending")
    approved_count = sum(1 for a in appointments if a.get("status") == "scheduled")
    rejected_count = sum(1 for a in appointments if a.get("status") == "cancelled")
    active_reminders = sum(1 for r in reminders if r.get("active", True))

    return {
        "appointments_per_week": {"labels": week_labels, "data": week_counts},
        "age_distribution":  {"labels": list(age_buckets.keys()), "data": list(age_buckets.values())},
        "disease_categories": {"labels": list(top_diseases.keys()) or ["No Data"],
                               "data": list(top_diseases.values()) or [0]},
        "consultation_trends": {"labels": trend_labels, "data": trend_counts},
        "gender_distribution": {"labels": list(genders.keys()), "data": list(genders.values())},
        "appointment_types":  {"labels": list(appt_types.keys()) or ["None"],
                               "data": list(appt_types.values()) or [0]},
        "medicine_frequency": {"labels": list(top_meds.keys()) or ["None"],
                               "data": list(top_meds.values()) or [0]},
        "summary": {
            "total_patients":        len(patients),
            "total_appointments":    len(appointments),
            "total_consultations":   len(consultations),
            "today_appointments":    sum(1 for a in appointments if a.get("date") == today.isoformat()),
            "pending_appointments":  pending_count,
            "approved_appointments": approved_count,
            "rejected_appointments": rejected_count,
            "active_reminders":      active_reminders,
        }
    }
