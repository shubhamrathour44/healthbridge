from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import random, httpx
from jose import jwt

from ..database import get_db
from ..models.user import User, UserRole
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Schemas ───────────────────────────────────────────────

class SendOTPRequest(BaseModel):
    phone: str

class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str
    name: str = ""  # only needed on first login

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str


# ── Helpers ───────────────────────────────────────────────

def make_token(user_id: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def send_otp_sms(phone: str, otp: str):
    if not settings.MSG91_AUTH_KEY:
        # Dev mode — print to terminal, no SMS sent
        print(f"\n[DEV OTP] ☎  {phone}  →  {otp}\n")
        return
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://api.msg91.com/api/v5/otp",
            params={
                "authkey": settings.MSG91_AUTH_KEY,
                "mobile": f"91{phone}",
                "otp": otp,
                "template_id": settings.MSG91_TEMPLATE_ID,
            },
        )


def clean_phone(raw: str) -> str:
    phone = raw.strip().lstrip("+")
    if phone.startswith("91") and len(phone) == 12:
        phone = phone[2:]
    return phone


# ── Routes ────────────────────────────────────────────────

@router.post("/send-otp")
async def send_otp(payload: SendOTPRequest, db: AsyncSession = Depends(get_db)):
    phone = clean_phone(payload.phone)
    if len(phone) != 10 or not phone.isdigit():
        raise HTTPException(400, "Enter a valid 10-digit Indian mobile number")

    otp = str(random.randint(100000, 999999))
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)

    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()

    if not user:
        user = User(name="", phone=phone, role=UserRole.patient)
        db.add(user)

    user.otp_code = otp
    user.otp_expires_at = expires
    await db.commit()

    await send_otp_sms(phone, otp)
    return {"message": "OTP sent", "expires_in": 600}


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(payload: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    phone = clean_phone(payload.phone)

    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()

    if not user or not user.otp_code:
        raise HTTPException(400, "No OTP requested for this number")

    if datetime.now(timezone.utc) > user.otp_expires_at:
        raise HTTPException(400, "OTP expired — request a new one")

    if user.otp_code != payload.otp.strip():
        raise HTTPException(400, "Incorrect OTP")

    # First-time user — save name if provided
    if not user.name and payload.name:
        user.name = payload.name

    # Clear OTP after successful use
    user.otp_code = None
    user.otp_expires_at = None
    await db.commit()

    return TokenResponse(
        access_token=make_token(str(user.id), user.role),
        role=user.role,
        user_id=str(user.id),
    )


@router.get("/me")
async def get_me(db: AsyncSession = Depends(get_db)):
    # Wired properly once middleware is imported
    return {"message": "Use Authorization: Bearer <token>"}
