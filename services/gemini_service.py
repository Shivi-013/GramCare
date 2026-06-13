import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in .env file")
        _client = genai.Client(api_key=api_key)
    return _client


def _generate(prompt: str) -> str:
    client = _get_client()
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )
    return response.text.strip()


def analyze_symptoms(symptoms: str, age: int = None, gender: str = None) -> dict:
    try:
        context = f"Patient age: {age}, Gender: {gender}. " if age else ""
        prompt = f"""
You are an AI medical assistant for rural healthcare. Analyze the following symptoms and provide a structured response.

{context}Symptoms: {symptoms}

Respond ONLY with a valid JSON object in exactly this format:
{{
  "possible_conditions": ["condition1", "condition2", "condition3"],
  "severity": "Low|Medium|High|Emergency",
  "severity_reason": "Brief explanation of severity",
  "recommendations": ["recommendation1", "recommendation2", "recommendation3"],
  "when_to_seek_care": "Immediate|Within 24 hours|Within a week|Monitor at home",
  "home_remedies": ["remedy1", "remedy2"],
  "warning_signs": ["sign1", "sign2"],
  "emergency": false
}}

Set emergency to true ONLY if symptoms include chest pain, stroke, difficulty breathing, or similar life-threatening conditions.
"""
        text = _generate(prompt)
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        return {
            "possible_conditions": ["Unable to analyze - please consult a doctor"],
            "severity": "Medium",
            "severity_reason": f"AI analysis unavailable: {str(e)}",
            "recommendations": ["Visit nearest healthcare facility", "Consult a licensed physician"],
            "when_to_seek_care": "Within 24 hours",
            "home_remedies": ["Rest and stay hydrated"],
            "warning_signs": ["Worsening symptoms"],
            "emergency": False
        }


def triage_patient(age: int, symptoms: str, duration: str, existing_conditions: str = "") -> dict:
    try:
        prompt = f"""
You are a medical triage AI for a rural telemedicine system. Assess the following patient and assign priority.

Patient Age: {age}
Symptoms: {symptoms}
Duration of symptoms: {duration}
Existing medical conditions: {existing_conditions or "None"}

Respond ONLY with a valid JSON object in exactly this format:
{{
  "priority": "Low|Medium|High|Emergency",
  "priority_score": 1-10,
  "triage_notes": "Brief clinical notes",
  "recommended_action": "What to do next",
  "estimated_wait_time": "Immediate|30 minutes|2 hours|Today|This week",
  "specialist_needed": "General Physician|Cardiologist|Neurologist|Pediatrician|None",
  "vitals_to_check": ["vital1", "vital2"],
  "emergency": false
}}

Set priority to Emergency and emergency to true if there is immediate life threat.
"""
        text = _generate(prompt)
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        return {
            "priority": "Medium",
            "priority_score": 5,
            "triage_notes": f"Manual triage required - AI unavailable: {str(e)}",
            "recommended_action": "Consult duty doctor for manual assessment",
            "estimated_wait_time": "2 hours",
            "specialist_needed": "General Physician",
            "vitals_to_check": ["Blood Pressure", "Temperature", "Pulse Rate", "SpO2"],
            "emergency": False
        }


SPECIALTY_LIST = [
    "General Physician", "Cardiologist", "Gynecologist", "Neurologist",
    "Orthopedic", "Dermatologist", "Pediatrician", "ENT",
    "Psychiatrist", "Ophthalmologist",
]


def suggest_doctor_from_symptoms(symptoms: str, age: int = None, gender: str = None) -> dict:
    try:
        ctx = f"Patient age: {age}, Gender: {gender}. " if age else ""
        prompt = f"""
You are an AI medical assistant for rural telemedicine. Analyze symptoms and suggest the right doctor.

{ctx}Patient symptoms: {symptoms}

Available specialties (use EXACTLY one): {", ".join(SPECIALTY_LIST)}

Respond ONLY with a valid JSON object in this exact format:
{{
  "possible_conditions": ["condition1", "condition2", "condition3"],
  "suggested_specialty": "exact specialty from list",
  "urgency": "Immediate|Within 24 hours|Within 3 days|Within a week",
  "urgency_color": "red|orange|yellow|green",
  "explanation": "One sentence why this specialist is recommended.",
  "also_consider": "optional second specialty or empty string",
  "home_care": ["tip1", "tip2"],
  "warning_signs": ["sign1", "sign2"],
  "emergency": false
}}

Rules:
- suggested_specialty MUST exactly match one value from the list.
- emergency=true only for chest pain, stroke, severe breathing difficulty, loss of consciousness.
- urgency_color: red=Immediate, orange=24h, yellow=3days, green=week.
"""
        text = _generate(prompt)
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        return {
            "possible_conditions": ["Unable to analyze — please consult a doctor"],
            "suggested_specialty": "General Physician",
            "urgency": "Within 24 hours",
            "urgency_color": "orange",
            "explanation": f"AI analysis unavailable. Please visit a General Physician. ({str(e)})",
            "also_consider": "",
            "home_care": ["Rest and stay hydrated", "Monitor your temperature"],
            "warning_signs": ["Worsening symptoms", "High fever above 103°F"],
            "emergency": False,
        }


def generate_health_summary(patient: dict, consultations: list) -> str:
    try:
        consultation_text = "\n".join([
            f"- Date: {c['date']}, Diagnosis: {c['diagnosis']}, Symptoms: {c['symptoms']}"
            for c in consultations[-5:]
        ]) or "No previous consultations"
        prompt = f"""
Generate a concise health summary for a rural patient record.

Patient: {patient['name']}, Age: {patient['age']}, Gender: {patient['gender']}
Blood Group: {patient.get('blood_group', 'Unknown')}

Recent consultations:
{consultation_text}

Write a professional 3-4 sentence health summary suitable for a medical report. Focus on patterns and recommendations.
"""
        return _generate(prompt)
    except Exception as e:
        return f"Health summary unavailable. Please consult patient records directly. ({str(e)})"
