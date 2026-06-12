from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from ..database import get_db
from ..models.hospital import Hospital, HospitalStatus
from ..models.doctor import Doctor
from ..models.user import User, UserRole
from ..middleware.auth import get_current_user, require_role

router = APIRouter(prefix="/hospitals", tags=["hospitals"])


# ── Public: only approved hospitals ──────────────────────

@router.get("/")
async def search_hospitals(
    q: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    specialty: Optional[str] = Query(None),
    limit: int = Query(20, le=50),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Hospital).where(Hospital.status == HospitalStatus.approved)
    if q:
        stmt = stmt.where(Hospital.name.ilike(f"%{q}%"))
    if city:
        stmt = stmt.where(Hospital.city.ilike(f"%{city}%"))
    if specialty:
        stmt = stmt.where(Hospital.specialties.any(specialty))
    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    hospitals = result.scalars().all()
    return {"hospitals": hospitals, "count": len(hospitals)}


@router.get("/{hospital_id}")
async def get_hospital(hospital_id: str, db: AsyncSession = Depends(get_db)):
    h = await db.get(Hospital, hospital_id)
    if not h or h.status != HospitalStatus.approved:
        raise HTTPException(404, "Hospital not found")
    return h


@router.get("/{hospital_id}/doctors")
async def get_hospital_doctors(hospital_id: str, db: AsyncSession = Depends(get_db)):
    h = await db.get(Hospital, hospital_id)
    if not h or h.status != HospitalStatus.approved:
        raise HTTPException(404, "Hospital not found")
    result = await db.execute(
        select(Doctor).where(
            Doctor.hospital_id == hospital_id,
            Doctor.is_active == True,
        )
    )
    return {"doctors": result.scalars().all()}


# ── Self-registration ─────────────────────────────────────

class HospitalRegisterRequest(BaseModel):
    name: str
    address: str
    city: str
    state: str
    phone: str
    whatsapp: str = ""
    specialties: list[str] = []
    lat: Optional[float] = None
    lng: Optional[float] = None


@router.post("/register")
async def register_hospital(
    payload: HospitalRegisterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    slug = (
        payload.name.lower().replace(" ", "-")
        + "-"
        + payload.city.lower().replace(" ", "-")
    )
    # Ensure slug uniqueness
    existing = await db.execute(select(Hospital).where(Hospital.slug == slug))
    if existing.scalar_one_or_none():
        slug = slug + "-" + str(current_user.id)[:8]

    h = Hospital(
        **payload.model_dump(),
        slug=slug,
        owner_id=current_user.id,
        status=HospitalStatus.pending,
    )
    db.add(h)
    await db.commit()
    await db.refresh(h)
    return {
        "message": "Registration submitted for admin review",
        "hospital_id": str(h.id),
        "status": "pending",
    }


# ── Admin: approval queue ─────────────────────────────────

@router.get(
    "/admin/pending",
    dependencies=[Depends(require_role(UserRole.superadmin))],
)
async def list_pending(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Hospital)
        .where(Hospital.status == HospitalStatus.pending)
        .order_by(Hospital.id)
    )
    return {"hospitals": result.scalars().all()}


@router.get(
    "/admin/all",
    dependencies=[Depends(require_role(UserRole.superadmin))],
)
async def list_all_hospitals(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Hospital)
    if status:
        stmt = stmt.where(Hospital.status == status)
    result = await db.execute(stmt)
    return {"hospitals": result.scalars().all()}


class ApprovalRequest(BaseModel):
    action: str   # "approve" | "reject" | "suspend"
    reason: str = ""


@router.post("/admin/{hospital_id}/review")
async def review_hospital(
    hospital_id: str,
    payload: ApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin)),
):
    h = await db.get(Hospital, hospital_id)
    if not h:
        raise HTTPException(404, "Hospital not found")

    if payload.action == "approve":
        h.status = HospitalStatus.approved
        h.approved_by = current_user.id
        h.approved_at = datetime.now(timezone.utc)
        h.rejection_reason = None
    elif payload.action == "reject":
        if not payload.reason:
            raise HTTPException(400, "Rejection reason is required")
        h.status = HospitalStatus.rejected
        h.rejection_reason = payload.reason
    elif payload.action == "suspend":
        h.status = HospitalStatus.suspended
        h.rejection_reason = payload.reason or "Suspended by admin"
    else:
        raise HTTPException(400, "action must be: approve | reject | suspend")

    await db.commit()
    return {"hospital_id": hospital_id, "status": h.status}
