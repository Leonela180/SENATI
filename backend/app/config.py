import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]          # carpeta lumia-ai/
load_dotenv(ROOT / ".env")


def _path(var, default):
    value = os.getenv(var) or default
    return (ROOT / value).resolve()


class Config:
    APP_ENV = os.getenv("APP_ENV", "development")
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "")
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    PRIVATE_STORAGE_ROOT = _path("PRIVATE_STORAGE_ROOT", "./private_data")
    MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
    MAX_CONTENT_LENGTH = (MAX_UPLOAD_MB + 1) * 1024 * 1024     # Flask corta antes de leer más
    MAX_IMAGE_PIXELS = int(os.getenv("MAX_IMAGE_PIXELS", "24000000"))

    AI_ENGINE = os.getenv("AI_ENGINE", "mock")                 # local | mock
    AI_MODEL_ID = os.getenv("AI_MODEL_ID", "")
    AI_MODEL_PATH = _path("AI_MODEL_PATH", "./models/no-configurado")
    AI_WORKER_CONCURRENCY = int(os.getenv("AI_WORKER_CONCURRENCY", "1"))
    AI_MAX_ATTEMPTS = 3                                        # reintentos limitados (RNF-08)
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    # Generación de imágenes con Gemini (servicio EXTERNO: requiere consentimiento en cada solicitud)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
    GEMINI_TIMEOUT = int(os.getenv("GEMINI_TIMEOUT", "90"))

    # Compartir por internet (scripts/compartir.ps1): confiar en las cabeceras del túnel para conocer la IP
    # real de cada visitante (límite de intentos por persona) y el https del enlace público.
    TRUST_PROXY = os.getenv("TRUST_PROXY", "0") == "1"

    # Horario y horas: zona horaria de la empresa (Perú, UTC−5, sin horario de verano)
    APP_TZ_OFFSET_HOURS = int(os.getenv("APP_TZ_OFFSET_HOURS", "-5"))

    # Sesión y cookies (RNF-01)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = APP_ENV == "production"            # True solo si se sirve por HTTPS
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    WTF_CSRF_HEADERS = ["X-CSRFToken"]
    WTF_CSRF_TIME_LIMIT = None
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_HEADERS_ENABLED = True
