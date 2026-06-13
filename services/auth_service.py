import hashlib
from services.storage_service import read_json, write_json, generate_id, now_iso


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed


def get_user_by_username(username: str) -> dict | None:
    return next((u for u in read_json("data/users.json") if u.get("username") == username), None)


def get_user_by_id(user_id: str) -> dict | None:
    return next((u for u in read_json("data/users.json") if u.get("id") == user_id), None)


def authenticate(username: str, password: str) -> dict | None:
    user = get_user_by_username(username)
    if user and verify_password(password, user["password_hash"]):
        return user
    return None


def register_patient(name: str, phone: str, age: int, gender: str,
                     address: str, blood_group: str, password: str) -> tuple:
    patients = read_json("data/patients.json")
    users    = read_json("data/users.json")

    if any(u.get("username") == phone for u in users):
        raise ValueError("An account with this phone number already exists.")

    patient = {
        "id":          generate_id("P", patients),
        "name":        name,
        "age":         age,
        "gender":      gender,
        "phone":       phone,
        "address":     address,
        "blood_group": blood_group,
        "created_at":  now_iso()
    }
    patients.append(patient)
    write_json("data/patients.json", patients)

    users = read_json("data/users.json")
    user = {
        "id":            generate_id("U", users),
        "username":      phone,
        "password_hash": hash_password(password),
        "role":          "patient",
        "name":          name,
        "patient_id":    patient["id"],
        "phone":         phone,
        "created_at":    now_iso()
    }
    users.append(user)
    write_json("data/users.json", users)
    return patient, user


def update_doctor_profile(data: dict, user_id: str = None) -> dict:
    """Update doctor profile. If user_id provided, updates that specific doctor;
    otherwise updates the first doctor found (legacy behaviour)."""
    users = read_json("data/users.json")
    for i, u in enumerate(users):
        if u.get("role") == "doctor" and (user_id is None or u.get("id") == user_id):
            users[i].update(data)
            write_json("data/users.json", users)
            return users[i]
    return {}


# ── Default doctors ────────────────────────────────────────────────────────────
_DEFAULT_DOCTORS = [
    {
        "id": "D001", "username": "doctor",
        "name": "Dr. Anjali Sharma", "specialization": "General Physician",
        "qualifications": "MBBS, MD (General Medicine)", "experience": "12 years",
        "phone": "9876500001", "email": "anjali@gramcare.in",
        "bio": "Dedicated rural healthcare physician with 12 years of experience.",
        "reg_number": "MCI-2012-45678", "clinic_name": "GramCare Primary Health Centre",
        "clinic_address": "Village Dharampur, Rajasthan",
    },
    {
        "id": "D002", "username": "dr.rajesh",
        "name": "Dr. Rajesh Patel", "specialization": "General Physician",
        "qualifications": "MBBS, MD, FCGP", "experience": "8 years",
        "phone": "9876500002", "email": "rajesh@gramcare.in",
        "bio": "Family medicine specialist with focus on preventive care.",
        "reg_number": "MCI-2016-78901", "clinic_name": "GramCare Primary Health Centre",
        "clinic_address": "Village Dharampur, Rajasthan",
    },
    {
        "id": "D003", "username": "dr.priya",
        "name": "Dr. Priya Nair", "specialization": "Cardiologist",
        "qualifications": "MBBS, MD, DM (Cardiology)", "experience": "10 years",
        "phone": "9876500003", "email": "priya@gramcare.in",
        "bio": "Interventional cardiologist specialising in rural cardiac care.",
        "reg_number": "MCI-2014-34567", "clinic_name": "GramCare Heart Clinic",
        "clinic_address": "Village Dharampur, Rajasthan",
    },
    {
        "id": "D004", "username": "dr.arjun",
        "name": "Dr. Arjun Gupta", "specialization": "Cardiologist",
        "qualifications": "MBBS, DNB (Cardiology)", "experience": "7 years",
        "phone": "9876500004", "email": "arjun@gramcare.in",
        "bio": "Focused on preventive cardiology and hypertension management.",
        "reg_number": "MCI-2017-56789", "clinic_name": "GramCare Heart Clinic",
        "clinic_address": "Village Dharampur, Rajasthan",
    },
    {
        "id": "D005", "username": "dr.meera",
        "name": "Dr. Meera Singh", "specialization": "Gynecologist",
        "qualifications": "MBBS, MS (Obstetrics & Gynecology)", "experience": "15 years",
        "phone": "9876500005", "email": "meera@gramcare.in",
        "bio": "Senior OB-GYN with extensive experience in maternal and reproductive health.",
        "reg_number": "MCI-2009-12345", "clinic_name": "GramCare Women's Clinic",
        "clinic_address": "Village Dharampur, Rajasthan",
    },
    {
        "id": "D006", "username": "dr.kavya",
        "name": "Dr. Kavya Iyer", "specialization": "Gynecologist",
        "qualifications": "MBBS, MD (Gynecology)", "experience": "6 years",
        "phone": "9876500006", "email": "kavya@gramcare.in",
        "bio": "Specialises in high-risk pregnancy and laparoscopic surgery.",
        "reg_number": "MCI-2018-23456", "clinic_name": "GramCare Women's Clinic",
        "clinic_address": "Village Dharampur, Rajasthan",
    },
    {
        "id": "D007", "username": "dr.suresh",
        "name": "Dr. Suresh Mehta", "specialization": "Neurologist",
        "qualifications": "MBBS, MD, DM (Neurology)", "experience": "11 years",
        "phone": "9876500007", "email": "suresh@gramcare.in",
        "bio": "Expert in epilepsy, stroke, and neurodegenerative disorders.",
        "reg_number": "MCI-2013-67890", "clinic_name": "GramCare Neuro Centre",
        "clinic_address": "Village Dharampur, Rajasthan",
    },
    {
        "id": "D008", "username": "dr.vikram",
        "name": "Dr. Vikram Malhotra", "specialization": "Orthopedic",
        "qualifications": "MBBS, MS (Orthopedics), DNB", "experience": "9 years",
        "phone": "9876500008", "email": "vikram@gramcare.in",
        "bio": "Joint replacement and sports injury specialist.",
        "reg_number": "MCI-2015-89012", "clinic_name": "GramCare Ortho Clinic",
        "clinic_address": "Village Dharampur, Rajasthan",
    },
    {
        "id": "D009", "username": "dr.sunita",
        "name": "Dr. Sunita Rao", "specialization": "Dermatologist",
        "qualifications": "MBBS, MD (Dermatology)", "experience": "8 years",
        "phone": "9876500009", "email": "sunita@gramcare.in",
        "bio": "Skin disorders, hair loss, and cosmetic dermatology specialist.",
        "reg_number": "MCI-2016-90123", "clinic_name": "GramCare Skin Clinic",
        "clinic_address": "Village Dharampur, Rajasthan",
    },
    {
        "id": "D010", "username": "dr.rohan",
        "name": "Dr. Rohan Verma", "specialization": "Pediatrician",
        "qualifications": "MBBS, MD (Pediatrics), DCH", "experience": "10 years",
        "phone": "9876500010", "email": "rohan@gramcare.in",
        "bio": "Child health specialist with focus on rural immunisation and nutrition.",
        "reg_number": "MCI-2014-01234", "clinic_name": "GramCare Child Clinic",
        "clinic_address": "Village Dharampur, Rajasthan",
    },
    {
        "id": "D011", "username": "dr.arun",
        "name": "Dr. Arun Pillai", "specialization": "ENT",
        "qualifications": "MBBS, MS (ENT)", "experience": "9 years",
        "phone": "9876500011", "email": "arun@gramcare.in",
        "bio": "Ear, nose, throat surgeon with expertise in hearing disorders.",
        "reg_number": "MCI-2015-12345", "clinic_name": "GramCare ENT Clinic",
        "clinic_address": "Village Dharampur, Rajasthan",
    },
    {
        "id": "D012", "username": "dr.deepak",
        "name": "Dr. Deepak Nair", "specialization": "Psychiatrist",
        "qualifications": "MBBS, MD (Psychiatry)", "experience": "7 years",
        "phone": "9876500012", "email": "deepak@gramcare.in",
        "bio": "Mental health specialist focused on rural community wellbeing.",
        "reg_number": "MCI-2017-23456", "clinic_name": "GramCare Mind Wellness",
        "clinic_address": "Village Dharampur, Rajasthan",
    },
    {
        "id": "D013", "username": "dr.ritu",
        "name": "Dr. Ritu Sharma", "specialization": "Ophthalmologist",
        "qualifications": "MBBS, MS (Ophthalmology), DOMS", "experience": "8 years",
        "phone": "9876500013", "email": "ritu@gramcare.in",
        "bio": "Cataract surgery and vision care specialist for rural communities.",
        "reg_number": "MCI-2016-34567", "clinic_name": "GramCare Eye Centre",
        "clinic_address": "Village Dharampur, Rajasthan",
    },
]


def setup_default_users():
    users    = read_json("data/users.json")
    patients = read_json("data/patients.json")
    changed  = False

    existing_usernames = {u.get("username") for u in users}

    for doc in _DEFAULT_DOCTORS:
        if doc["username"] not in existing_usernames:
            users.append({
                "id":             doc["id"],
                "username":       doc["username"],
                "password_hash":  hash_password("doctor123"),
                "role":           "doctor",
                "name":           doc["name"],
                "specialization": doc["specialization"],
                "qualifications": doc["qualifications"],
                "experience":     doc["experience"],
                "phone":          doc["phone"],
                "email":          doc["email"],
                "bio":            doc["bio"],
                "reg_number":     doc["reg_number"],
                "clinic_name":    doc["clinic_name"],
                "clinic_address": doc["clinic_address"],
                "created_at":     now_iso(),
            })
            existing_usernames.add(doc["username"])
            changed = True

    for p in patients:
        username = p["phone"]
        if username not in existing_usernames:
            users.append({
                "id":            generate_id("U", users),
                "username":      username,
                "password_hash": hash_password("patient123"),
                "role":          "patient",
                "name":          p["name"],
                "patient_id":    p["id"],
                "phone":         p["phone"],
                "created_at":    now_iso()
            })
            existing_usernames.add(username)
            changed = True

    if changed:
        write_json("data/users.json", users)
