from sqlalchemy import Column, String, Float, Boolean, ARRAY, ForeignKey, DateTime, Text, Enum as PgEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid, enum
from ..database import Base


class HospitalStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    suspended = "suspended"


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    lat = Column(Float)
    lng = Column(Float)
    phone = Column(String)
    whatsapp = Column(String)
    specialties = Column(ARRAY(String), default=[])
    status = Column(PgEnum(HospitalStatus), default=HospitalStatus.pending, nullable=False)

    # Audit fields
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Who registered this hospital
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    doctors = relationship("Doctor", back_populates="hospital")
    appointments = relationship("Appointment", back_populates="hospital")
    reviews = relationship("Review", back_populates="hospital")
