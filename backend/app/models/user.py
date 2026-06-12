from sqlalchemy import Column, String, Boolean, DateTime, Enum as PgEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid, enum
from ..database import Base


class UserRole(str, enum.Enum):
    patient = "patient"
    hospital_admin = "hospital_admin"
    superadmin = "superadmin"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    role = Column(PgEnum(UserRole), default=UserRole.patient)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default="now()")

    # OTP fields — no password
    otp_code = Column(String(6), nullable=True)
    otp_expires_at = Column(DateTime(timezone=True), nullable=True)

    appointments = relationship("Appointment", back_populates="patient")
    reviews = relationship("Review", back_populates="patient")
