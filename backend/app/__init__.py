from .database import Base

# Import all models here so Alembic autogenerate picks them up
from .models.user import User
from .models.hospital import Hospital
from .models.doctor import Doctor
from .models.appointment import Appointment
from .models.review import Review
