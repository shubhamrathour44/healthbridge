"""
Seed script — run after migrations:
  python seed.py
"""
import asyncio
from datetime import time
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings
from app.models.user import User, UserRole
from app.models.hospital import Hospital, HospitalStatus
from app.models.doctor import Doctor
from app.database import Base

engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
)
Session = async_sessionmaker(engine, expire_on_commit=False)

HOSPITALS = [
    {"name": "Apollo Hospital", "city": "Delhi", "state": "Delhi",
     "address": "Sarita Vihar, Mathura Road, New Delhi",
     "lat": 28.5274, "lng": 77.2868, "phone": "01126825500",
     "specialties": ["Cardiology", "Oncology", "Neurology", "Orthopedics"]},
    {"name": "Fortis Hospital", "city": "Delhi", "state": "Delhi",
     "address": "Sector B, Pocket 1, Aruna Asaf Ali Marg, Vasant Kunj",
     "lat": 28.5206, "lng": 77.1539, "phone": "01142776222",
     "specialties": ["Cardiology", "Neurology", "Gastroenterology"]},
    {"name": "Max Super Speciality Hospital", "city": "Delhi", "state": "Delhi",
     "address": "1, 2, Press Enclave Marg, Saket",
     "lat": 28.5275, "lng": 77.2083, "phone": "01126515050",
     "specialties": ["Oncology", "Transplant", "Orthopedics", "Pediatrics"]},
    {"name": "AIIMS", "city": "Delhi", "state": "Delhi",
     "address": "Sri Aurobindo Marg, Ansari Nagar",
     "lat": 28.5672, "lng": 77.2100, "phone": "01126588500",
     "specialties": ["All specialties", "Research", "Trauma"]},
    {"name": "Safdarjung Hospital", "city": "Delhi", "state": "Delhi",
     "address": "Ring Road, Safdarjung",
     "lat": 28.5685, "lng": 77.2064, "phone": "01126165060",
     "specialties": ["General Medicine", "Surgery", "Gynecology"]},
    {"name": "Kokilaben Dhirubhai Ambani Hospital", "city": "Mumbai", "state": "Maharashtra",
     "address": "Four Bungalows, Andheri West",
     "lat": 19.1239, "lng": 72.8387, "phone": "02230999999",
     "specialties": ["Cardiology", "Oncology", "Neurosciences", "Transplant"]},
    {"name": "Lilavati Hospital", "city": "Mumbai", "state": "Maharashtra",
     "address": "A-791, Bandra Reclamation, Bandra West",
     "lat": 19.0570, "lng": 72.8235, "phone": "02226751000",
     "specialties": ["Cardiology", "Orthopedics", "Oncology"]},
    {"name": "Breach Candy Hospital", "city": "Mumbai", "state": "Maharashtra",
     "address": "60-A, Bhulabhai Desai Road, Breach Candy",
     "lat": 18.9726, "lng": 72.8075, "phone": "02223667888",
     "specialties": ["General Medicine", "Surgery", "Maternity"]},
    {"name": "Hinduja Hospital", "city": "Mumbai", "state": "Maharashtra",
     "address": "Veer Savarkar Marg, Mahim",
     "lat": 19.0388, "lng": 72.8414, "phone": "02224455555",
     "specialties": ["Cardiology", "Neurology", "Orthopedics", "Urology"]},
    {"name": "Nanavati Max Super Speciality", "city": "Mumbai", "state": "Maharashtra",
     "address": "SV Road, Vile Parle West",
     "lat": 19.1001, "lng": 72.8370, "phone": "02226100000",
     "specialties": ["Oncology", "Cardiology", "Gastroenterology"]},
]

DOCTOR_TEMPLATES = [
    {"name": "Dr. Rajesh Kumar", "specialty": "Cardiology",
     "qualification": "MBBS, MD, DM (Cardiology)", "experience_years": 15,
     "consultation_fee": 800, "available_days": ["Monday","Wednesday","Friday"],
     "slot_start": time(9, 0), "slot_end": time(13, 0), "slot_duration_mins": 15},
    {"name": "Dr. Priya Sharma", "specialty": "Neurology",
     "qualification": "MBBS, MD, DM (Neurology)", "experience_years": 12,
     "consultation_fee": 1000, "available_days": ["Tuesday","Thursday","Saturday"],
     "slot_start": time(10, 0), "slot_end": time(14, 0), "slot_duration_mins": 20},
    {"name": "Dr. Amit Patel", "specialty": "Orthopedics",
     "qualification": "MBBS, MS (Ortho)", "experience_years": 10,
     "consultation_fee": 600, "available_days": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
     "slot_start": time(17, 0), "slot_end": time(20, 0), "slot_duration_mins": 15},
]

TEST_USERS = [
    {"name": "Rahul Verma", "phone": "9000000001", "role": UserRole.patient},
    {"name": "Sneha Singh", "phone": "9000000002", "role": UserRole.patient},
    {"name": "Admin User", "phone": "9000000099", "role": UserRole.superadmin},
]


async def seed():
    async with Session() as db:
        print("Creating test users...")
        users = []
        for u in TEST_USERS:
            user = User(**u)
            db.add(user)
            users.append(user)
        await db.flush()

        admin = users[-1]  # superadmin

        print("Creating hospitals...")
        for h_data in HOSPITALS:
            slug = h_data["name"].lower().replace(" ", "-") + "-" + h_data["city"].lower()
            hospital = Hospital(
                **h_data,
                slug=slug,
                whatsapp=h_data["phone"],
                status=HospitalStatus.approved,
                owner_id=users[0].id,
                approved_by=admin.id,
            )
            db.add(hospital)
            await db.flush()

            print(f"  Adding doctors to {h_data['name']}...")
            for i, tmpl in enumerate(DOCTOR_TEMPLATES):
                doc_data = {**tmpl}
                # Vary the doctor name slightly per hospital
                doc_data["name"] = tmpl["name"].replace("Dr. ", f"Dr. {chr(65+i)}-")
                doctor = Doctor(**doc_data, hospital_id=hospital.id)
                db.add(doctor)

        await db.commit()
        print("\nSeed complete!")
        print("Test accounts:")
        for u in TEST_USERS:
            print(f"  Phone: {u['phone']}  Role: {u['role']}")
        print("\nUse /auth/send-otp to get an OTP (prints to terminal in dev mode)")


if __name__ == "__main__":
    asyncio.run(seed())
