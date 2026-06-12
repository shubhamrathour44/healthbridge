from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from datetime import date, time, datetime, timedelta
from typing import Optional

from ..database import get_db
from ..models.appointment import Appointment, AppointmentStatus
from ..models.doctor import Doctor
from ..middleware.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/appointments", tags=["appointments"])

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def generate_slots(
    slot_start: time,
    slot_end: time,
    duration_mins: int,
    booked_times: set,
    target_date: date,
) -> list[dict]:
    slots = []
    current = datetime.combine(target_date, slot_start)
    end = datetime.combine(target_date, slot_end)
    now = datetime.now()

    while current < end:
        t = current.time()
        is_past = (target_date == date.today()) and (current <= now)
        slots.append({
            "time": t.strftime("%H:%M"),
            "available": t not in booked_times and not is_past,
        })
        current += timedelta(minutes=duration_mins)
    return slots


# ── Slots ─────────────────────────────────────────────────

@router.get("/slots/{doctor_id}/{appt_date}")
async def get_available_slots(
    doctor_id: str,
    appt_date: date,
    db: AsyncSession = Depends(get_db),
):
    doctor = await db.get(Doctor, doctor_id)
    if not doctor or not doctor.is_active:
        raise HTTPException(404, "Doctor not found or inactive")

    if appt_date < date.today():
        return {"slots": [], "reason": "Date is in the past"}

    if appt_date > date.today() + timedelta(days=30):
        return {"slots": [], "reason": "Booking window is 30 days ahead"}

    day_name = DAY_NAMES[appt_date.weekday()]
    if doctor.available_days and day_name not in doctor.available_days:
        return {
            "slots": [],
            "reason": f"Doctor not available on {day_name}",
            "available_days": doctor.available_days,
        }

    result = await db.execute(
        select(Appointment.appointment_time).where(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == appt_date,
                Appointment.status.notin_([AppointmentStatus.cancelled]),
            )
        )
    )
    booked_times = {r[0] for r in result.fetchall()}

    slots = generate_slots(
        doctor.slot_start,
        doctor.slot_end,
        doctor.slot_duration_mins or 15,
        booked_times,
        appt_date,
    )
    return {
        "doctor": doctor.name,
        "date": str(appt_date),
        "slots": slots,
        "total": len(slots),
        "available": sum(1 for s in slots if s["available"]),
    }


# ── Book ──────────────────────────────────────────────────

class BookAppointmentRequest(BaseModel):
    doctor_id: str
    hospital_id: str
    appointment_date: date
    appointment_time: time
    notes: str = ""


@router.post("/")
async def book_appointment(
    payload: BookAppointmentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doctor = await db.get(Doctor, payload.doctor_id)
    if not doctor or not doctor.is_active:
        raise HTTPException(404, "Doctor not found")

    if payload.appointment_date < date.today():
        raise HTTPException(400, "Cannot book in the past")

    day_name = DAY_NAMES[payload.appointment_date.weekday()]
    if doctor.available_days and day_name not in doctor.available_days:
        raise HTTPException(400, f"Doctor not available on {day_name}")

    if not (doctor.slot_start <= payload.appointment_time < doctor.slot_end):
        raise HTTPException(400, "Time is outside doctor's working hours")

    clash = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == payload.doctor_id,
                Appointment.appointment_date == payload.appointment_date,
                Appointment.appointment_time == payload.appointment_time,
                Appointment.status.notin_([AppointmentStatus.cancelled]),
            )
        )
    )
    if clash.scalar_one_or_none():
        raise HTTPException(409, "Slot already booked — please pick another time")

    appt = Appointment(
        patient_id=current_user.id,
        doctor_id=payload.doctor_id,
        hospital_id=payload.hospital_id,
        appointment_date=payload.appointment_date,
        appointment_time=payload.appointment_time,
        notes=payload.notes,
        fee_paid=doctor.consultation_fee,
    )
    db.add(appt)
    await db.commit()
    await db.refresh(appt)
    return appt


# ── My appointments ───────────────────────────────────────

@router.get("/mine")
async def my_appointments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Appointment)
        .where(Appointment.patient_id == current_user.id)
        .order_by(Appointment.appointment_date.desc())
    )
    return {"appointments": result.scalars().all()}


# ── Cancel ────────────────────────────────────────────────

@router.patch("/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appt = await db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(404, "Appointment not found")
    if str(appt.patient_id) != str(current_user.id):
        raise HTTPException(403, "Not your appointment")
    if appt.status == AppointmentStatus.completed:
        raise HTTPException(400, "Cannot cancel a completed appointment")
    if appt.status == AppointmentStatus.cancelled:
        raise HTTPException(400, "Already cancelled")

    appt.status = AppointmentStatus.cancelled
    await db.commit()
    return {"status": "cancelled", "appointment_id": appointment_id}
