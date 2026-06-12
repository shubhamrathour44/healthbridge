from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ..database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"), nullable=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=True)
    rating = Column(Integer, nullable=False)  # 1–5
    comment = Column(String)
    created_at = Column(DateTime(timezone=True), server_default="now()")

    patient = relationship("User", back_populates="reviews")
    hospital = relationship("Hospital", back_populates="reviews")
    doctor = relationship("Doctor", back_populates="reviews")
