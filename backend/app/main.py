from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, hospitals, doctors, appointments

app = FastAPI(
    title="HealthBridge API",
    version="1.0.0",
    description="Hospital discovery, appointment booking, and more.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(hospitals.router)
app.include_router(doctors.router)
app.include_router(appointments.router)


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "service": "healthbridge-api"}
