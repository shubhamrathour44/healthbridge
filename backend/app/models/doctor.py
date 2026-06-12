from sqlalchemy import Column, String, Integer, Boolean, ARRAY, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ..database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    name = Column(String, nullable=False)
    specialty = Column(String, nullable=False)
    qualification = Column(String)
    experience_years = Column(Integer, default=0)
    consultation_fee = Column(Integer, default=0)  # INR
    available_days = Column(ARRAY(String), default=[])  # ["Monday","Tuesday",...]
    slot_start = Column(Time)
    slot_end = Column(Time)
    slot_duration_mins = Column(Integer, default=15)
    is_active = Column(Boolean, default=True)

    hospital = relationship("Hospital", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")
    reviews = relationship("Review", back_populates="doctor")
