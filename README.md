# GramCare — Smart Telemedicine Platform for Rural India

GramCare is a full-stack telemedicine web application built with **FastAPI** and **Jinja2**, designed to bridge the healthcare gap in rural communities. It brings together AI-powered symptom analysis, appointment management, digital prescriptions, and a self-service patient portal — all without requiring a database server, using plain JSON file storage.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Doctor Roster](#doctor-roster)
- [AI Features](#ai-features)
- [PDF Generation](#pdf-generation)
- [Data Storage](#data-storage)
- [Multi-language Support](#multi-language-support)

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

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Shivi-013/GramCare.git
cd GramCare

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

Patient login uses their **phone number** as the username and `patient123` as the default password. New patients can register at `/auth/register`.

---

## AI Features

All AI features are powered by **Google Gemini** via the `google-genai` SDK.

### Symptom Analysis
Takes symptoms, age, and gender as input. Returns a structured analysis with:
- Possible conditions, severity level (Low / Medium / High / Emergency)
- Recommendations, home remedies, and warning signs
- Emergency flag for critical presentations

### AI Triage
Used by doctors to prioritise patients before consultation. Returns a priority score (1–10), estimated wait time, specialist recommendation, and vitals to check.

### Doctor Recommendation
Used in the patient portal symptom checker. Matches symptoms to one of GramCare's 10 specialisations and returns matching doctors from the roster along with urgency level and home care tips.

### Health Summary
Generates a short professional health summary from a patient's consultation history, used as the narrative section of AI health report PDFs.

### Emergency Detection
Before calling Gemini, the app checks symptoms for keywords such as `"chest pain"`, `"stroke"`, `"difficulty breathing"`, and `"unconscious"`. If matched, the response is automatically escalated to Emergency severity and an alert banner is shown, regardless of the AI result.

---

## PDF Generation

PDFs are built with **ReportLab** and saved to the `prescriptions/` directory.

### Prescription PDF
Contains patient details, diagnosis, symptoms, medicines with dosage instructions, and a doctor signature block.
Filename: `prescription_{consult_id}_{timestamp}.pdf`

### AI Health Report PDF
Contains patient summary, reported symptoms, AI analysis (conditions, severity, recommendations, warning signs), and doctor signature.
Filename: `health_report_{patient_id}_{timestamp}.pdf`

PDFs can be generated from the doctor's Reports page, or downloaded directly from the patient's Medicines and Reports pages.

---

## Data Storage

GramCare uses flat JSON files instead of a database. All files are created automatically on first run.

| File | Contents |
|---|---|
| `data/users.json` | All user accounts (doctors + patients) with hashed passwords |
| `data/patients.json` | Patient records: name, age, gender, phone, address, blood group |
| `data/appointments.json` | All appointments: patient, doctor, date, time, status, symptoms |
| `data/consultations.json` | Consultation records: diagnosis, medicines, notes, follow-up |
| `data/reminders.json` | Medicine reminders, auto-created when a consultation is saved |

IDs are auto-incremented with a prefix — `D001`–`D013` for doctors, `P001`+ for patients, `A001`+ for appointments, and so on. All passwords are stored as SHA-256 hashes.

---

## Multi-language Support

The UI ships with translation files for four languages:

| Language | File |
|---|---|
| English | `static/translations/en.json` |
| Hindi | `static/translations/hi.json` |
| Tamil | `static/translations/ta.json` |
| Telugu | `static/translations/te.json` |

Translation keys cover navigation labels, form fields, severity levels, and button text. The language switcher is available in the sidebar of both the doctor and patient layouts.

---

## License

This project is built for educational and demonstration purposes as part of a rural healthcare initiative. Feel free to fork, adapt, and deploy for non-commercial community health use.
