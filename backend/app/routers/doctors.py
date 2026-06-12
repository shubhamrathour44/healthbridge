from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel
from datetime import time

from ..database import get_db
from ..models.doctor import Doctor
from ..models.hospital import Hospital, HospitalStatus
from ..models.user import UserRole
from ..middleware.auth import get_current_user, require_role
from ..models.user import User

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/")
async def search_doctors(
    specialty: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    limit: int = Query(20, le=50),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Doctor)
        .join(Hospital, Doctor.hospital_id == Hospital.id)
        .where(
            Doctor.is_active == True,
            Hospital.status == HospitalStatus.approved,
        )
    )
    if specialty:
        stmt = stmt.where(Doctor.specialty.ilike(f"%{specialty}%"))
    if q:
        stmt = stmt.where(Doctor.name.ilike(f"%{q}%"))
    if city:
        stmt = stmt.where(Hospital.city.ilike(f"%{city}%"))

    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    return {"doctors": result.scalars().all()}


@router.get("/{doctor_id}")
async def get_doctor(doctor_id: str, db: AsyncSession = Depends(get_db)):
    doctor = await db.get(Doctor, doctor_id)
    if not doctor or not doctor.is_active:
        raise HTTPException(404, "Doctor not found")
    return doctor


# ── Hospital admin: manage their own doctors ──────────────

class DoctorCreateRequest(BaseModel):
    name: str
    specialty: str
    qualification: str = ""
    experience_years: int = 0
    consultation_fee: int = 0
    available_days: list[str] = []
    slot_start: time
    slot_end: time
    slot_duration_mins: int = 15


@router.post("/")
async def create_doctor(
    hospital_id: str,
    payload: DoctorCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.hospital_admin, UserRole.superadmin)),
):
    hospital = await db.get(Hospital, hospital_id)
    if not hospital:
        raise HTTPException(404, "Hospital not found")
    if (
        current_user.role == UserRole.hospital_admin
        and str(hospital.owner_id) != str(current_user.id)
    ):
        raise HTTPException(403, "Not your hospital")

    doctor = Doctor(**payload.model_dump(), hospital_id=hospital_id)
    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)
    return doctor


@router.patch("/{doctor_id}/toggle")
async def toggle_doctor(
    doctor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.hospital_admin, UserRole.superadmin)),
):
    doctor = await db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(404, "Doctor not found")
    doctor.is_active = not doctor.is_active
    await db.commit()
    return {"doctor_id": doctor_id, "is_active": doctor.is_active}
