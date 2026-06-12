from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # SMS — leave blank in dev, OTP prints to terminal instead
    MSG91_AUTH_KEY: str = ""
    MSG91_TEMPLATE_ID: str = ""

    GOOGLE_MAPS_API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
