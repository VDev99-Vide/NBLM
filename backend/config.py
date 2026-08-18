"""NBLM Configuration — loads from .env via python-dotenv."""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "NBLM")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    CF_ACCOUNT_ID: str = os.getenv("CF_ACCOUNT_ID", "")
    CF_R2_ACCESS_KEY: str = os.getenv("CF_R2_ACCESS_KEY", "")
    CF_R2_SECRET_KEY: str = os.getenv("CF_R2_SECRET_KEY", "")
    CF_R2_BUCKET: str = os.getenv("CF_R2_BUCKET", "nblm-storage")
    CF_R2_PUBLIC_URL: str = os.getenv("CF_R2_PUBLIC_URL", "")
    XKIRO_API_KEY: str = os.getenv("XKIRO_API_KEY", "")
    XKIRO_BASE_URL: str = os.getenv("XKIRO_BASE_URL", "https://api.xkiro.com/v1")
    XKIRO_CHAT_MODEL: str = os.getenv("XKIRO_CHAT_MODEL", "deepseek-v4")
    XKIRO_VISION_MODEL: str = os.getenv("XKIRO_VISION_MODEL", "qwen-vl-max")
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "change-me")
    ADMIN_TOKEN: str = os.getenv("ADMIN_TOKEN", "")
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    @property
    def r2_endpoint(self) -> str:
        return f"https://{self.CF_ACCOUNT_ID}.r2.cloudflarestorage.com"

    @property
    def async_db_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

settings = Settings()
