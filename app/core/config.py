from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    # DB
    DATABASE_URL: str

    # Auth / JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # App meta
    API_TITLE: str = "MediPlan API"
    API_VERSION: str = "0.1.0"

    UPLOAD_DIR: Path = Path("uploads")  # relativno u odnosu na CWD/app root
    MAX_UPLOAD_MB: int = 20
    ALLOWED_UPLOAD_EXTS: set[str] = {".pdf", ".jpg", ".jpeg", ".png"}

    # Pydantic v2 stil
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
