# GramCare — Smart Telemedicine Platform for Rural India

GramCare is a full-stack telemedicine web application built with **FastAPI** and **Jinja2**, designed to bridge the healthcare gap in rural communities. It brings together AI-powered symptom analysis, appointment management, digital prescriptions, and a self-service patient portal — all without requiring a database server, using plain JSON file storage.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Default Accounts](#default-accounts)
- [Doctor Roster](#doctor-roster)
- [Application Routes](#application-routes)
- [AI Features](#ai-features)
- [PDF Generation](#pdf-generation)
- [Data Storage](#data-storage)
- [Multi-language Support](#multi-language-support)
- [Screenshots](#screenshots)

---

## Features

### For Doctors
- **Dashboard** — personalised stats: today's appointments, total patients, consultations, active reminders; upcoming and pending appointment queue
- **Patient Management** — full patient records with medical history, search and filter
- **Appointments** — approve, reschedule, reject, or complete patient-requested appointments; book appointments directly for walk-in patients
- **Consultations** — record diagnosis, symptoms, medicines, recommended tests, and follow-up dates; auto-creates medicine reminders on save
- **AI Symptom Checker** — submit patient symptoms to Gemini AI and receive structured analysis: possible conditions, severity, recommendations, home remedies, and warning signs
- **AI Triage** — assign priority score (1–10) to patients before consultation; estimates wait time and specialist needed
- **Medicine Reminders** — view and manage all active patient medicine reminders
- **Analytics** — appointment and consultation statistics with Chart.js visualisations
- **Reports & Prescriptions** — generate prescription PDFs and AI health report PDFs; download any previous PDF

### For Patients
- **Self-service Portal** — dedicated patient-facing interface separate from the doctor dashboard
- **Appointment Booking** — browse doctors by specialisation, select preferred doctor, pick date/time and appointment type; cancel if needed
- **My Medicines** — view all prescribed medicines from completed consultations with PDF download per prescription
- **Reminders** — see all active medicine reminders set by doctors
- **Reports** — download consultation-linked prescription PDFs and AI-generated health reports
- **Medical Timeline** — chronological view of all appointments and consultations grouped by year with status colour-coding
- **AI Symptom Checker** — patients can check their own symptoms and get doctor recommendations before booking
- **Profile** — view personal details and change password

### Platform
- Cookie-based session authentication with SHA-256 password hashing
- Role-based access control (doctor / patient) with redirect guards on every route
- Emergency keyword detection that escalates AI severity to "Emergency" automatically
- Multi-language UI: English, Hindi (हिन्दी), Tamil (தமிழ்), Telugu (తెలుగు)
- Fully responsive Tailwind CSS design; works on desktop and mobile

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | [FastAPI](https://fastapi.tiangolo.com/) 0.111 |
| Template engine | Jinja2 3.1 |
| ASGI server | Uvicorn 0.29 |
| Session middleware | Starlette `SessionMiddleware` |
| AI / LLM | Google Gemini (`google-genai` SDK, model `gemini-flash-latest`) |
| PDF generation | ReportLab 4.2 |
| Image processing | Pillow 10.3 |
| Data persistence | JSON flat files (no database required) |
| Frontend | Tailwind CSS (CDN), Font Awesome 6.5, Chart.js, Inter font |
| Environment | python-dotenv |

---

## Project Structure

```
GramCare/
│
├── app.py                        # FastAPI app entry point, middleware, route registration
│
├── routes/
│   ├── auth.py                   # Login, logout, register
│   ├── patient_portal.py         # All patient-facing pages (/portal/*)
│   ├── patients.py               # Doctor: patient list and detail
│   ├── appointments.py           # Doctor: appointment management
│   ├── consultations.py          # Doctor: consultation recording and detail
│   ├── ai_features.py            # Doctor: AI symptom checker and triage
│   ├── reminders.py              # Doctor: medicine reminders view
│   ├── analytics.py              # Doctor: analytics dashboard
│   └── reports.py                # Doctor: PDF generation and download
│
├── services/
│   ├── auth_service.py           # Password hashing, authentication, default user seeding
│   ├── storage_service.py        # JSON read/write, ID generation, CRUD helpers
│   ├── gemini_service.py         # Gemini AI client, symptom analysis, triage, health summary
│   └── report_service.py         # ReportLab prescription and health report PDF builders
│
├── templates/
│   ├── base.html                 # Doctor-side base layout (sidebar, nav)
│   ├── base_patient.html         # Patient portal base layout
│   ├── landing.html              # Public landing page
│   ├── login.html                # Login page (role-switching doctor/patient)
│   ├── register.html             # Patient registration
│   ├── dashboard.html            # Doctor dashboard
│   ├── patients.html             # Patient list
│   ├── patient_detail.html       # Single patient record (doctor view)
│   ├── appointments.html         # Appointment management (doctor)
│   ├── consultation.html         # Consultation list + new form (doctor)
│   ├── consultation_detail.html  # Consultation detail (doctor view)
│   ├── ai_symptoms.html          # AI symptom checker (doctor)
│   ├── ai_triage.html            # AI triage (doctor)
│   ├── reminders.html            # Reminders list (doctor)
│   ├── analytics.html            # Analytics (doctor)
│   ├── reports.html              # Reports and PDF generator (doctor)
│   ├── doctor_profile.html       # Doctor profile editor
│   ├── patient_dashboard.html    # Patient portal home
│   ├── patient_appointments.html # Patient: book and view appointments
│   ├── patient_medicines.html    # Patient: prescribed medicines
│   ├── patient_reminders.html    # Patient: medicine reminders
│   ├── patient_reports.html      # Patient: download PDFs
│   ├── patient_timeline.html     # Patient: chronological medical history
│   ├── patient_symptoms.html     # Patient: AI symptom checker
│   ├── patient_profile.html      # Patient: profile and password change
│   └── consultation_detail_patient.html  # Consultation detail (patient view)
│
├── static/
│   ├── assets/                   # Images
│   │   ├── login_page.jpg
│   │   ├── dashboard_pic.jpg
│   │   ├── GramCare.png
│   │   └── landingpage_photo.jpg
│   ├── css/style.css
│   ├── js/
│   │   ├── main.js
│   │   └── charts.js
│   └── translations/
│       ├── en.json
│       ├── hi.json
│       ├── ta.json
│       └── te.json
│
├── data/                         # Auto-created on first run
│   ├── users.json
│   ├── patients.json
│   ├── appointments.json
│   ├── consultations.json
│   └── reminders.json
│
├── prescriptions/                # Auto-created; generated PDFs stored here
│
├── .env                          # Secret keys and config (not committed)
├── .env.example                  # Template for .env
└── requirements.txt
```

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/gramcare.git
cd gramcare

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install the new Google Gemini SDK (required for AQ. API keys)
pip install google-genai

# 5. Copy the environment template and fill in your values
cp .env.example .env
```

### Running the App

```bash
python app.py
```

The server starts at **http://localhost:8000** by default.

Alternatively, run with uvicorn directly:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

On first startup, the app automatically:
- Creates the `data/`, `uploads/`, and `prescriptions/` directories
- Seeds all 13 default doctors into `data/users.json`

---

## Configuration

Copy `.env.example` to `.env` and set the following:

```env
# Required for AI features
GEMINI_API_KEY=your_gemini_api_key_here

# Optional — defaults shown
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
```

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click **"Get API key"** → **"Create API key"**
4. Copy the key (it will start with `AQ.` — this is the new secure format)
5. Paste it into your `.env` file as `GEMINI_API_KEY=AQ.your_key_here`

> **Note:** GramCare uses the `google-genai` SDK (v2.8.0+), which supports the new `AQ.` key format. The older `google-generativeai` package does not work with these keys.

---

## Default Accounts

All default passwords can be changed after logging in.

### Doctor Login

| Field | Value |
|---|---|
| Username | `doctor` (or any doctor username — see table below) |
| Password | `doctor123` |

### Patient Login

| Field | Value |
|---|---|
| Username | Patient's **phone number** |
| Password | `patient123` (default; can be changed in profile) |

To register a new patient, visit **`/auth/register`** or use the "Create account" link on the login page.

---

## Doctor Roster

13 specialist doctors are seeded automatically on first run. All share the password `doctor123`.

| Username | Name | Specialisation |
|---|---|---|
| `doctor` | Dr. Anjali Sharma | General Physician |
| `dr.rajesh` | Dr. Rajesh Patel | General Physician |
| `dr.priya` | Dr. Priya Nair | Cardiologist |
| `dr.arjun` | Dr. Arjun Gupta | Cardiologist |
| `dr.meera` | Dr. Meera Singh | Gynecologist |
| `dr.kavya` | Dr. Kavya Iyer | Gynecologist |
| `dr.suresh` | Dr. Suresh Mehta | Neurologist |
| `dr.vikram` | Dr. Vikram Malhotra | Orthopedic |
| `dr.sunita` | Dr. Sunita Rao | Dermatologist |
| `dr.rohan` | Dr. Rohan Verma | Pediatrician |
| `dr.arun` | Dr. Arun Pillai | ENT |
| `dr.deepak` | Dr. Deepak Nair | Psychiatrist |
| `dr.ritu` | Dr. Ritu Sharma | Ophthalmologist |

Each doctor's dashboard, appointment queue, and consultation history is scoped to their own specialisation and ID.

---

## Application Routes

### Public

| Route | Description |
|---|---|
| `GET /` | Landing page |
| `GET /auth/login` | Login page (role-switching tabs) |
| `POST /auth/login` | Authenticate and create session |
| `GET /auth/register` | Patient registration form |
| `POST /auth/register` | Create patient account |
| `GET /auth/logout` | Destroy session and redirect |

### Doctor Portal (`/dashboard`, `/patients`, `/appointments`, `/consultations`, `/ai`, `/reminders`, `/analytics`, `/reports`)

| Route | Description |
|---|---|
| `GET /dashboard` | Doctor home dashboard |
| `GET /patients/` | Patient list |
| `GET /patients/{id}` | Patient detail and history |
| `GET /appointments/` | Appointment management |
| `POST /appointments/book` | Doctor books appointment for patient |
| `POST /appointments/{id}/approve` | Approve pending appointment |
| `POST /appointments/{id}/reject` | Reject with reason |
| `POST /appointments/{id}/complete` | Mark as completed |
| `GET /consultations/` | Consultation list + new form |
| `POST /consultations/add` | Record new consultation |
| `GET /consultations/{id}` | Consultation detail |
| `GET /ai/symptoms` | AI symptom checker form |
| `POST /ai/symptoms/check` | Submit symptoms to Gemini |
| `GET /ai/triage` | AI triage form |
| `POST /ai/triage/assess` | Submit for triage scoring |
| `GET /reminders/` | Medicine reminders list |
| `GET /analytics/` | Analytics charts and stats |
| `GET /reports/` | Report generator page |
| `POST /reports/prescription` | Generate prescription PDF (form) |
| `POST /reports/health-report` | Generate AI health report PDF (form) |
| `GET /reports/prescription/{consult_id}` | Auto-generate prescription PDF from consultation |
| `GET /reports/health-report/{patient_id}` | Auto-generate AI health report for patient |
| `GET /reports/download/{filename}` | Download any PDF by filename |

### Patient Portal (`/portal/*`)

| Route | Description |
|---|---|
| `GET /portal/` | Patient dashboard |
| `GET /portal/appointments` | View and book appointments |
| `POST /portal/appointments/book` | Submit booking request |
| `POST /portal/appointments/{id}/cancel` | Cancel an appointment |
| `GET /portal/medicines` | Prescribed medicines from consultations |
| `GET /portal/reminders` | Active medicine reminders |
| `GET /portal/reports` | Reports and PDF download |
| `GET /portal/reports/download/{filename}` | Download PDF |
| `GET /portal/timeline` | Chronological medical history |
| `GET /portal/symptoms` | Patient AI symptom checker |
| `POST /portal/symptoms/check` | Submit symptoms |
| `GET /portal/profile` | Profile page |
| `POST /portal/profile/change-password` | Change password |

---

## AI Features

All AI features are powered by **Google Gemini** via the `google-genai` SDK.

### Symptom Analysis (`analyze_symptoms`)
Takes symptoms, age, and gender as input. Returns a structured JSON with:
- `possible_conditions` — list of likely diagnoses
- `severity` — Low / Medium / High / Emergency
- `severity_reason` — brief explanation
- `recommendations` — actionable next steps
- `when_to_seek_care` — urgency timeline
- `home_remedies` — supportive care tips
- `warning_signs` — red flags to watch for
- `emergency` — boolean flag

### AI Triage (`triage_patient`)
Used by doctors to prioritise patients. Returns:
- `priority` — Low / Medium / High / Emergency
- `priority_score` — 1 to 10
- `triage_notes` — clinical summary
- `recommended_action` — what to do next
- `estimated_wait_time`
- `specialist_needed`
- `vitals_to_check`

### Doctor Recommendation (`suggest_doctor_from_symptoms`)
Used in the patient portal symptom checker. Returns:
- `suggested_specialty` — matched to GramCare's 10-speciality list
- `urgency` + `urgency_color`
- `possible_conditions`
- `home_care` tips
- `warning_signs`
- Matching doctors from the roster are shown automatically

### Health Summary (`generate_health_summary`)
Generates a 3–4 sentence professional health summary from a patient's consultation history, used as the narrative section of AI health report PDFs.

### Emergency Detection
Before calling Gemini, the app checks the symptoms text for keywords such as `"chest pain"`, `"stroke"`, `"difficulty breathing"`, `"unconscious"`, and others. If matched, the AI response is overridden to `severity: Emergency` and an emergency banner is shown to the user, regardless of what Gemini returns.

---

## PDF Generation

PDFs are built with **ReportLab** in `services/report_service.py` and saved to the `prescriptions/` directory.

### Prescription PDF
- Header with GramCare logo, clinic name, and registration number
- Patient details: name, age, gender, blood group
- Diagnosis and symptoms
- Medicines table with dosage instructions
- Doctor signature block

Filename format: `prescription_{consult_id}_{timestamp}.pdf`

### AI Health Report PDF
- Patient summary block
- Symptoms reported
- AI analysis: possible conditions, severity rating
- Recommendations section
- Warning signs
- Doctor's signature

Filename format: `health_report_{patient_id}_{timestamp}.pdf`

PDFs can be triggered:
- From the doctor's Reports page (manual form)
- Directly from the patient's Medicines page (per-consultation link)
- Directly from the patient's Reports page (per-patient health report)

---

## Data Storage

GramCare uses flat JSON files instead of a database. All files are created automatically.

| File | Contents |
|---|---|
| `data/users.json` | All user accounts (doctors + patients) with hashed passwords |
| `data/patients.json` | Patient records: name, age, gender, phone, address, blood group |
| `data/appointments.json` | All appointments: patient, doctor, date, time, status, symptoms |
| `data/consultations.json` | Consultation records: diagnosis, medicines, notes, follow-up |
| `data/reminders.json` | Medicine reminders, auto-created when a consultation is saved |

### ID format
IDs are auto-incremented with a prefix: `D001`–`D013` for doctors, `P001`... for patients, `A001`... for appointments, `C001`... for consultations, `R001`... for reminders, `U001`... for user accounts.

### Passwords
All passwords are stored as SHA-256 hashes. No plain-text passwords are ever written to disk.

---

## Multi-language Support

The UI ships with translation files for four languages:

| Language | File |
|---|---|
| English | `static/translations/en.json` |
| Hindi | `static/translations/hi.json` |
| Tamil | `static/translations/ta.json` |
| Telugu | `static/translations/te.json` |

Translation keys cover all navigation labels, form fields, severity levels, and button text. The language switcher is available in the sidebar of both the doctor and patient layouts.

---

## Screenshots

| Page | Description |
|---|---|
| Landing | Public home page with feature overview |
| Login | Role-switching login (Doctor / Patient tabs) |
| Doctor Dashboard | Stats cards, upcoming appointments, recent consultations |
| Patient Portal | Appointment booking, medicines, timeline, AI symptom check |
| AI Symptom Checker | Gemini-powered analysis with severity badge and recommendations |
| Medical Timeline | Year-grouped chronological view of appointments and consultations |
| PDF Prescription | ReportLab-generated prescription with doctor details |

---

## License

This project is built for educational and demonstration purposes as part of a rural healthcare initiative. Feel free to fork, adapt, and deploy for non-commercial community health use.

---

*Built with care for rural India — ग्रामकेयर | கிராம்கேர் | గ్రామ్‌కేర్*
