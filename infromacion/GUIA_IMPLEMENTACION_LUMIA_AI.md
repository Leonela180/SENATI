# Guía de implementación paso a paso — LUMIA AI (v2)

**Proyecto:** «Mejora de piel con IA» · Plataforma **LUMIA AI** · THINKABLE LABS
**Para qué sirve:** construir tú misma, desde una carpeta vacía, todo el sistema que describe el informe, siguiendo el **SKILL LUMIA AI V7**, hasta instalarlo en otra PC y obtener las evidencias que faltan en el informe.

> **Regla de oro (del skill):** el sistema, el informe y el skill deben decir lo mismo. Si al construir algo cambias un nombre, una tabla o un endpoint, anótalo en `docs/estado.md` y luego lo corregimos en el informe. Nunca se inventan resultados: lo que no se probó se marca como «pendiente».

---

## Índice

- [0. Antes de empezar: lo que debe coincidir](#0-antes-de-empezar-lo-que-debe-coincidir)
- [1. F0 — Preparar la PC y diagnosticar el hardware (A01–A02)](#1-f0--preparar-la-pc-y-diagnosticar-el-hardware-a01a02)
- [2. Crear el repositorio](#2-crear-el-repositorio)
- [3. PostgreSQL 17 (A05)](#3-postgresql-17-a05)
- [4. Backend: entorno, configuración y fábrica Flask (A05)](#4-backend-entorno-configuración-y-fábrica-flask-a05)
- [5. Modelos SQLAlchemy y migraciones Alembic (A05)](#5-modelos-sqlalchemy-y-migraciones-alembic-a05)
- [6. Servicios: permisos, imágenes, trabajos y equipos (A04–A06)](#6-servicios-permisos-imágenes-trabajos-y-equipos-a04a06)
- [7. API REST completa (A04–A07)](#7-api-rest-completa-a04a07)
- [8. Motor de IA (F3 — A08–A09)](#8-motor-de-ia-f3--a08a09)
- [9. Worker (A07)](#9-worker-a07)
- [10. Frontend React + TypeScript + Tailwind + shadcn/ui (A04, A07)](#10-frontend-react--typescript--tailwind--shadcnui-a04-a07)
- [11. Pruebas automatizadas: pytest, Vitest y Playwright (A10)](#11-pruebas-automatizadas-pytest-vitest-y-playwright-a10)
- [12. Scripts PowerShell (A11)](#12-scripts-powershell-a11)
- [13. Evaluación del motor con el protocolo del Anexo A (A09)](#13-evaluación-del-motor-con-el-protocolo-del-anexo-a-a09)
- [14. Instalación en otra PC (CP-14, A11)](#14-instalación-en-otra-pc-cp-14-a11)
- [15. Documentación del repositorio (docs/)](#15-documentación-del-repositorio-docs)
- [16. Lista de evidencias y qué cambiar en el informe (A12)](#16-lista-de-evidencias-y-qué-cambiar-en-el-informe-a12)
- [17. Solución de problemas](#17-solución-de-problemas)

---

## 0. Antes de empezar: lo que debe coincidir

| Elemento | Informe / Skill | Dónde se construye |
|---|---|---|
| 7 casos de uso CU01–CU07 (G01–G07) | Cap. IV, Tabla de CU | Pasos 6, 7 y 10 |
| 21 requerimientos funcionales (RF-01 a RF-17 = MVP; RF-18 a RF-21 = segunda fase) | Tabla RF | Pasos 6 y 7 |
| 10 requerimientos no funcionales (RNF-01 a RNF-10) | Tabla RNF | Pasos 4, 9, 11 y 12 |
| 8 tablas: users, workspaces, team_memberships, team_invitations, images, processing_jobs, audit_events, service_incidents | Diccionario de datos, IDEF1X | Paso 5 |
| Estados del trabajo: queued, processing, completed, failed | 4.1.2 | Pasos 7 y 9 |
| Límites: JPG/PNG/WebP, ≤ 10 MB, ≤ 24 MP | RF-06, CU03 | Paso 6 |
| Parámetros del motor: fuerza 0,20–0,40; 25–35 pasos; guía 5–7; semilla fija; 512–768 px | Anexo D | Paso 8 |
| Endpoints `/api/v1/...` | Anexo E, Tabla E1 | Paso 7 |
| Variables `.env` | Anexo E | Paso 2 |
| Casos de prueba CP-01 a CP-14 | 4.5.11 | Pasos 11 y 12 |
| Scripts diagnostico, instalar, iniciar, detener y verificar `.ps1` | 4.5.12, RNF-09 | Paso 12 |

**Fases del skill y actividades del cronograma del informe:**

| Fase | Actividades del cronograma | Pasos de esta guía |
|---|---|---|
| F0 Inspección | A01 muestras · A02 hardware y requisitos | 1 |
| F1 Producto navegable | A03 UML/datos · A04 landing, login, perfil · A05 PostgreSQL y permisos | 2–7, 10 |
| F2 Flujo completo | A06 carga y cola · A07 worker, historial, comparador, descarga | 6–10 (con `AI_ENGINE=mock`) |
| F3 Humanización real | A08 investigación de motores · A09 integración y evaluación | 8, 13 |
| F4 Extras | Equipos, invitaciones, estadísticas, admin (CU05–CU07) | 6, 7, 10 |
| F5 Entrega | A10 pruebas · A11 scripts e instalación · A12 informe | 11, 12, 14–16 |

**Orden recomendado de trabajo:** haz todo con `AI_ENGINE=mock` hasta el paso 11 (el circuito completo funcionando). Después instala el motor real (paso 8.5), cambia a `AI_ENGINE=local` y evalúa (paso 13). Así, si la IA da problemas, el resto ya está listo.

**Cómo crear los archivos:** usa **Visual Studio Code** (https://code.visualstudio.com/). Cada bloque de código de esta guía empieza con la ruta del archivo; créalo con ese nombre exacto y pega el contenido completo.

**Guarda tu avance con Git** al terminar cada paso:

```powershell
git add -A; git commit -m "Paso N: descripción"
```

---

## 1. F0 — Preparar la PC y diagnosticar el hardware (A01–A02)

### 1.1 Instalar los programas

1. **Git**: https://git-scm.com/download/win
2. **Python 3.12** (64 bits). Marca «Add python.exe to PATH»: https://www.python.org/downloads/windows/
3. **Node.js LTS**: https://nodejs.org/
4. **PostgreSQL 17** (incluye pgAdmin). Anota la contraseña del usuario `postgres` y deja el puerto 5432: https://www.postgresql.org/download/windows/
5. **Controlador NVIDIA** actualizado: https://www.nvidia.com/Download/index.aspx
6. **Visual Studio Code**.

### 1.2 Comprobar

```powershell
git --version
python --version          # Python 3.12.x
node --version; npm --version
psql --version            # psql (PostgreSQL) 17.x
nvidia-smi                # nombre de la GPU, VRAM y versión de CUDA del controlador
```

> Si `psql` no se reconoce, agrega `C:\Program Files\PostgreSQL\17\bin` al PATH (Configuración → Sistema → Información → Configuración avanzada → Variables de entorno), cierra y vuelve a abrir PowerShell.

Permite la ejecución de scripts locales (solo una vez):

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 1.3 Registrar el hardware (evidencia para A02 y para `docs/motor-ia.md`)

```powershell
Get-CimInstance Win32_Processor | Select-Object Name
"RAM GB: " + [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB,1)
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
Get-PSDrive C | Select-Object Used,Free
(Get-CimInstance Win32_ComputerSystem).Model     # modelo exacto de tu laptop
```

📌 **Anota:** el modelo exacto de la laptop, su CPU, GPU, VRAM y RAM, y el precio de compra real (boleta o factura). El informe asume «Lenovo LOQ 15 · RTX 4050 6 GB · S/ 3 999»; si tu laptop es otra, se corrige en el paso 16.

### 1.4 Muestras (A01)

Crea una carpeta **fuera del repositorio**, por ejemplo `C:\lumia_muestras\`, y reúne entre **15 y 30 imágenes de personas generadas por IA que tengas permiso de usar**. Busca variedad de tonos de piel, edades aparentes, iluminación y planos (busto, medio y entero). Nómbralas `M01.png`, `M02.jpg`, etc. Para cada una anota su defecto principal (piel, ojos, cabello, luz, manos u otro).

---

## 2. Crear el repositorio

```powershell
mkdir C:\proyectos\lumia-ai; cd C:\proyectos\lumia-ai
git init
mkdir backend, frontend, scripts, docs, models, private_data\originals, private_data\results
```

Estructura objetivo (skill §4 y Anexo E del informe):

```text
lumia-ai/
├── README.md · .gitignore · .env.example
├── docs/          estado, arquitectura, modelo-datos, permisos, motor-ia, desarrollo-local, instalacion-otra-pc
├── frontend/      React + TypeScript + Vite (src/app, pages, components, features, lib, styles, tests)
├── backend/       pyproject.toml, alembic.ini, migrations/, app/, tests/, tools/
│   └── app/       config, extensions, models/, api/, services/, ai/, workers/, storage/, security/
├── scripts/       diagnostico.ps1, instalar.ps1, iniciar.ps1, detener.ps1, verificar.ps1
├── models/        pesos del modelo (fuera de Git)
└── private_data/  originals/, results/ (fuera de Git)
```

**`.gitignore`**

```gitignore
# Python
__pycache__/
*.pyc
*.egg-info/
backend/.venv/
.pytest_cache/
# Node
frontend/node_modules/
frontend/dist/
frontend/test-results/
frontend/playwright-report/
# Secretos, datos privados y pesos
.env
private_data/
models/
scripts/.pids
*.log
```

**`.env.example`** (es el mismo del Anexo E; se sube a Git **sin secretos**):

```dotenv
APP_ENV=development
SECRET_KEY=
DATABASE_URL=
PRIVATE_STORAGE_ROOT=./private_data
MAX_UPLOAD_MB=10
MAX_IMAGE_PIXELS=24000000
AI_ENGINE=local
AI_MODEL_ID=
AI_MODEL_PATH=
AI_WORKER_CONCURRENCY=1
FRONTEND_ORIGIN=http://localhost:5173
```

Copia el archivo como **`.env`** (este nunca se sube) y complétalo:

```powershell
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"     # copia el resultado en SECRET_KEY
```

Tu `.env` de desarrollo debe quedar así (con tus valores):

```dotenv
APP_ENV=development
SECRET_KEY=pega_aqui_los_64_caracteres
DATABASE_URL=postgresql+psycopg://lumia_app:TU_CLAVE@localhost:5432/lumia
PRIVATE_STORAGE_ROOT=./private_data
MAX_UPLOAD_MB=10
MAX_IMAGE_PIXELS=24000000
AI_ENGINE=mock
AI_MODEL_ID=stable-diffusion-v1-5
AI_MODEL_PATH=./models/stable-diffusion-v1-5
AI_WORKER_CONCURRENCY=1
FRONTEND_ORIGIN=http://localhost:5173
```

> Empieza con `AI_ENGINE=mock` y cámbialo a `local` en el paso 8.5. En la contraseña de la base **no uses el carácter `%`**, porque rompe la lectura de Alembic.

---

## 3. PostgreSQL 17 (A05)

Crea un usuario **sin privilegios de administrador** (RNF-01) y dos bases: `lumia` (la real) y `lumia_test` (la de las pruebas automáticas).

```powershell
psql -U postgres
```

```sql
CREATE USER lumia_app WITH PASSWORD 'TU_CLAVE';
CREATE DATABASE lumia OWNER lumia_app ENCODING 'UTF8';
CREATE DATABASE lumia_test OWNER lumia_app ENCODING 'UTF8';
\q
```

Comprueba que el usuario entra:

```powershell
psql -U lumia_app -d lumia -c "SELECT current_user, version();"
```

Las tablas **no se crean a mano**: las crea Alembic en el paso 5.

---

## 4. Backend: entorno, configuración y fábrica Flask (A05)

### 4.1 Entorno virtual

```powershell
cd C:\proyectos\lumia-ai\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # verás (.venv) al inicio de la línea
python -m pip install --upgrade pip
```

### 4.2 `backend/pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "lumia-ai-backend"
version = "0.1.0"
requires-python = ">=3.12,<3.13"
dependencies = [
  "Flask>=3.1,<3.2",
  "Flask-SQLAlchemy>=3.1,<3.2",
  "SQLAlchemy>=2.0,<2.1",
  "alembic>=1.14,<2",
  "psycopg[binary]>=3.2,<3.3",
  "Flask-WTF>=1.2,<1.3",
  "Flask-Limiter>=3.8,<4",
  "Flask-Cors>=5,<6",
  "argon2-cffi>=23.1",
  "python-dotenv>=1.0",
  "Pillow>=11,<12",
  "waitress>=3,<4",
]

[project.optional-dependencies]
dev = ["pytest>=8"]
ia = ["diffusers>=0.31,<1", "transformers>=4.46,<5", "accelerate>=1.0", "safetensors>=0.4", "lpips>=0.1.4"]

[tool.setuptools.packages.find]
include = ["app*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

```powershell
pip install -e ".[dev]"
```

> Las dependencias de IA (`.[ia]` y PyTorch) se instalan en el paso 8.5.

### 4.3 Crear las carpetas y los `__init__.py` vacíos

```powershell
cd C:\proyectos\lumia-ai\backend
mkdir app\models, app\api, app\services, app\ai, app\workers, app\storage, app\security, tests, tools
"" | Out-File -Encoding utf8 app\storage\__init__.py
"" | Out-File -Encoding utf8 app\security\__init__.py
"" | Out-File -Encoding utf8 app\services\__init__.py
"" | Out-File -Encoding utf8 app\ai\__init__.py
"" | Out-File -Encoding utf8 app\workers\__init__.py
"" | Out-File -Encoding utf8 tests\__init__.py
```

(`app/__init__.py`, `app/models/__init__.py` y `app/api/__init__.py` tienen contenido y se crean más abajo.)

### 4.4 `backend/app/config.py`

```python
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

    # Sesión y cookies (RNF-01)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = APP_ENV == "production"            # True solo si se sirve por HTTPS
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    WTF_CSRF_HEADERS = ["X-CSRFToken"]
    WTF_CSRF_TIME_LIMIT = None
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_HEADERS_ENABLED = True
```

### 4.5 `backend/app/extensions.py`

```python
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=[])


def utc_now():
    return datetime.now(timezone.utc)
```

### 4.6 `backend/app/api/__init__.py` (formato de respuesta del skill §6)

```python
from flask import jsonify


def ok(data=None, status=200):
    return jsonify(data=data, error=None), status


def fail(code, message, status):
    return jsonify(data=None, error={"code": code, "message": message}), status
```

### 4.7 `backend/app/__init__.py` (fábrica de la aplicación)

```python
import logging
import time
import click
from flask import Flask, abort, jsonify, send_from_directory
from flask_cors import CORS
from flask_wtf.csrf import CSRFError
from sqlalchemy import text
from werkzeug.exceptions import HTTPException
from .config import Config, ROOT
from .extensions import db, csrf, limiter

log = logging.getLogger("lumia")


def create_app(config_object=Config, **overrides):
    app = Flask(__name__, static_folder=None)     # nada de rutas estáticas para imágenes (skill §6)
    app.config.from_object(config_object)
    app.config.update(overrides)
    if not app.config["SECRET_KEY"] or not app.config["SQLALCHEMY_DATABASE_URI"]:
        raise RuntimeError("Faltan SECRET_KEY o DATABASE_URL en .env")
    storage = app.config["PRIVATE_STORAGE_ROOT"]
    for sub in ("originals", "results"):
        (storage / sub).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": [app.config["FRONTEND_ORIGIN"]]}}, supports_credentials=True)

    from .api import auth, users, images, jobs, teams, admin
    for module in (auth, users, images, jobs, teams, admin):
        app.register_blueprint(module.bp, url_prefix="/api/v1")

    # ---------- Errores con formato uniforme y sin trazas internas (RF-12) ----------
    @app.errorhandler(CSRFError)
    def _csrf_error(e):
        return jsonify(data=None, error={"code": "csrf", "message": "Falta o venció el token de seguridad. Recarga la página."}), 403

    @app.errorhandler(HTTPException)
    def _http_error(e):
        return jsonify(data=None, error={"code": e.name.lower().replace(" ", "_"), "message": e.description}), e.code

    @app.errorhandler(Exception)
    def _unexpected(e):
        log.exception("Error no controlado")
        return jsonify(data=None, error={"code": "error_interno", "message": "Ocurrió un error. Inténtalo de nuevo."}), 500

    # ---------- Salud ----------
    @app.get("/api/v1/health")
    def health():
        db.session.execute(text("SELECT 1"))
        from .ai.prompts import PRESETS
        beat = storage / "worker.heartbeat"
        worker_age = round(time.time() - beat.stat().st_mtime) if beat.exists() else None
        return jsonify(data={
            "status": "ok",
            "engine": app.config["AI_ENGINE"],
            # Los presets se ofrecen solo con el motor real (skill §1.4)
            "presets": list(PRESETS) if app.config["AI_ENGINE"] == "local" else [],
            "worker_seconds_since_beat": worker_age,
        }, error=None)

    # ---------- Modo demostración: Flask sirve el frontend compilado ----------
    dist = ROOT / "frontend" / "dist"

    @app.get("/")
    @app.get("/<path:path>")
    def spa(path=""):
        if path.startswith("api/"):
            abort(404)
        if path and (dist / path).is_file():
            return send_from_directory(dist, path)
        if (dist / "index.html").is_file():
            return send_from_directory(dist, "index.html")
        return "Frontend no compilado: ejecuta 'npm run build' en frontend/ o usa http://localhost:5173", 503

    # ---------- Comando para crear el administrador técnico ----------
    @app.cli.command("crear-admin")
    @click.argument("email")
    def crear_admin(email):
        """Convierte en administrador a un usuario ya registrado."""
        from .models import User, audit
        user = db.session.query(User).filter_by(email=email.strip().lower()).first()
        if not user:
            raise click.ClickException("Primero registra ese correo desde la web.")
        user.global_role = "admin"
        audit(None, "user.promote_admin", "user", user.id)
        db.session.commit()
        click.echo(f"{email} ahora es administrador.")

    return app
```

### 4.8 `backend/wsgi.py`

```python
from app import create_app

app = create_app()
```

---

## 5. Modelos SQLAlchemy y migraciones Alembic (A05)

Los modelos siguen **exactamente** el diccionario de datos del informe y el esquema del skill §5.

### 5.1 `backend/app/models/user.py`

```python
from datetime import datetime
from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db, utc_now


class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    global_role: Mapped[str] = mapped_column(String(20), nullable=False, server_default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)
    __table_args__ = (CheckConstraint("global_role IN ('user','admin')", name="ck_users_global_role"),)
```

### 5.2 `backend/app/models/workspace.py`

```python
from datetime import datetime
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db, utc_now


class Workspace(db.Model):
    __tablename__ = "workspaces"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    __table_args__ = (
        CheckConstraint("kind IN ('personal','team')", name="ck_workspaces_kind"),
        # Un solo espacio personal por usuario: índice único parcial (AK del IDEF1X)
        Index("uq_workspaces_personal_owner", "owner_user_id", unique=True,
              postgresql_where=text("kind = 'personal'")),
    )


class TeamMembership(db.Model):
    __tablename__ = "team_memberships"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    team_workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)   # 1 equipo activo
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    __table_args__ = (CheckConstraint("role IN ('owner','member')", name="ck_team_memberships_role"),)


class TeamInvitation(db.Model):
    __tablename__ = "team_invitations"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    team_workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
```

### 5.3 `backend/app/models/image.py`

```python
from datetime import datetime
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db, utc_now


class Image(db.Model):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    original_storage_key: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)
    byte_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="ai_generated")  # declaración, no detector
    visibility: Mapped[str] = mapped_column(String(16), nullable=False, server_default="private")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    __table_args__ = (
        CheckConstraint("byte_size > 0", name="ck_images_byte_size"),
        CheckConstraint("width > 0 AND height > 0", name="ck_images_dimensions"),
        CheckConstraint("visibility IN ('private','team')", name="ck_images_visibility"),
        Index("ix_images_owner_created", "owner_user_id", "created_at"),
        Index("ix_images_workspace_created", "workspace_id", "created_at"),
    )
```

### 5.4 `backend/app/models/job.py`

```python
from datetime import datetime
from sqlalchemy import (BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text,
                        UniqueConstraint, text)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db, utc_now


class ProcessingJob(db.Model):
    __tablename__ = "processing_jobs"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"), nullable=False)
    requested_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="queued")
    model_id: Mapped[str | None] = mapped_column(String(120))
    model_version: Mapped[str | None] = mapped_column(String(80))
    preset: Mapped[str] = mapped_column(String(40), nullable=False, server_default="natural")
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    idempotency_key: Mapped[str] = mapped_column(String(100), nullable=False)
    result_storage_key: Mapped[str | None] = mapped_column(Text, unique=True)
    error_code: Mapped[str | None] = mapped_column(String(60))
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    image = relationship("Image")

    __table_args__ = (
        CheckConstraint("status IN ('queued','processing','completed','failed')", name="ck_jobs_status"),
        CheckConstraint("attempt_count >= 0", name="ck_jobs_attempt_count"),
        # RNF-07: completed solo con archivo de resultado registrado
        CheckConstraint("status <> 'completed' OR result_storage_key IS NOT NULL", name="ck_jobs_completed_result"),
        UniqueConstraint("requested_by", "idempotency_key", name="uq_jobs_requested_by_idempotency"),
        Index("ix_jobs_status_created", "status", "created_at"),
    )
```

### 5.5 `backend/app/models/audit.py`

```python
from datetime import datetime
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db, utc_now


class AuditEvent(db.Model):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    entity_id: Mapped[int | None] = mapped_column(BigInteger)
    # "metadata" está reservado en SQLAlchemy: el atributo es metadata_, la columna sigue siendo metadata
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class ServiceIncident(db.Model):
    __tablename__ = "service_incidents"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    service_name: Mapped[str] = mapped_column(String(60), nullable=False)
    error_code: Mapped[str] = mapped_column(String(60), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="open")
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (CheckConstraint("status IN ('open','resolved')", name="ck_service_incidents_status"),)


def audit(actor_id, action, entity_type, entity_id=None, **meta):
    """RF-17: registra una acción relevante. Nunca guardar contraseñas, tokens ni imágenes."""
    db.session.add(AuditEvent(actor_user_id=actor_id, action=action, entity_type=entity_type,
                              entity_id=entity_id, metadata_=meta))
```

### 5.6 `backend/app/models/__init__.py`

```python
from .user import User
from .workspace import Workspace, TeamMembership, TeamInvitation
from .image import Image
from .job import ProcessingJob
from .audit import AuditEvent, ServiceIncident, audit

__all__ = ["User", "Workspace", "TeamMembership", "TeamInvitation", "Image", "ProcessingJob",
           "AuditEvent", "ServiceIncident", "audit"]
```

### 5.7 Alembic

```powershell
cd C:\proyectos\lumia-ai\backend
alembic init migrations
```

1. En **`alembic.ini`**, deja la línea así: `sqlalchemy.url =` (vacía).
2. En **`migrations/env.py`**, busca la línea `target_metadata = None` y reemplázala por:

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from app import create_app
from app.extensions import db
import app.models  # noqa: F401  (registra las 8 tablas)

_flask_app = create_app()
config.set_main_option("sqlalchemy.url", _flask_app.config["SQLALCHEMY_DATABASE_URI"])
target_metadata = db.metadata
```

3. Genera y aplica la migración inicial:

```powershell
alembic revision --autogenerate -m "esquema inicial LUMIA AI"
alembic upgrade head
psql -U lumia_app -d lumia -c "\dt"
```

Debes ver las **8 tablas** y además `alembic_version`. Abre el archivo nuevo de `migrations/versions/` y comprueba que contiene `uq_workspaces_personal_owner` con `postgresql_where`.

📌 **Evidencia:** captura de `\dt` y de `\d processing_jobs` (muestra los CHECK, UNIQUE y FK). Sirve para confirmar el modelo de datos del informe (el skill pide que el DER coincida con las migraciones verificadas).

> Desde ahora, cualquier cambio del esquema se hace con `alembic revision --autogenerate -m "..."` y `alembic upgrade head`. Nunca edites tablas a mano.

---

## 6. Servicios: permisos, imágenes, trabajos y equipos (A04–A06)

### 6.1 `backend/app/storage/local_private.py`

```python
import secrets
from pathlib import Path
from flask import current_app

KINDS = ("originals", "results")


def new_key(ext: str) -> str:
    return f"{secrets.token_hex(16)}.{ext}"            # nombre aleatorio, sin datos del usuario (RF-08)


def path_for(kind: str, key: str) -> Path:
    if kind not in KINDS or not key or "/" in key or "\\" in key or ".." in key:
        raise ValueError("clave de almacenamiento inválida")   # evita path traversal
    return current_app.config["PRIVATE_STORAGE_ROOT"] / kind / key


def save_bytes(kind: str, key: str, data: bytes) -> None:
    path_for(kind, key).write_bytes(data)
```

### 6.2 `backend/app/security/uploads.py`

```python
import io
from PIL import Image as PILImage, UnidentifiedImageError
from flask import current_app

ALLOWED = {"JPEG": ("image/jpeg", "jpg"), "PNG": ("image/png", "png"), "WEBP": ("image/webp", "webp")}


class UploadError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code, self.message = code, message


def validate_image(file_storage) -> dict:
    """RF-06: valida por bytes reales, tamaño, píxeles y decodificación completa (no por extensión)."""
    max_mb = current_app.config["MAX_UPLOAD_MB"]
    max_px = current_app.config["MAX_IMAGE_PIXELS"]
    data = file_storage.read(max_mb * 1024 * 1024 + 1)
    if not data:
        raise UploadError("archivo_vacio", "El archivo está vacío.")
    if len(data) > max_mb * 1024 * 1024:
        raise UploadError("archivo_grande", f"El archivo supera {max_mb} MB.")
    PILImage.MAX_IMAGE_PIXELS = max_px * 2           # Pillow corta las «bombas» de descompresión
    try:
        probe = PILImage.open(io.BytesIO(data))
        fmt, (w, h) = probe.format, probe.size
        probe.verify()
        if fmt not in ALLOWED:
            raise UploadError("tipo_no_permitido", "Solo se aceptan imágenes JPG, PNG o WebP.")
        if w * h > max_px:
            raise UploadError("demasiados_pixeles", f"La imagen supera {max_px // 1_000_000} megapíxeles.")
        PILImage.open(io.BytesIO(data)).load()       # decodificación completa
    except UploadError:
        raise
    except (UnidentifiedImageError, OSError, SyntaxError, PILImage.DecompressionBombError):
        raise UploadError("imagen_invalida", "El archivo no es una imagen JPG, PNG o WebP válida.")
    mime, ext = ALLOWED[fmt]
    return {"bytes": data, "mime": mime, "ext": ext, "width": w, "height": h}
```

### 6.3 `backend/app/services/permission_service.py`

```python
from functools import wraps
from flask import abort, g, session
from ..extensions import db
from ..models import Image, ProcessingJob, TeamMembership, User, Workspace


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        uid = session.get("user_id")
        user = db.session.get(User, uid) if uid else None
        if not user or not user.is_active:
            abort(401, description="Inicia sesión para continuar.")
        g.user = user
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if g.user.global_role != "admin":
            abort(403, description="Solo el administrador técnico puede ver esta sección.")   # CU07 flujo 1a
        return fn(*args, **kwargs)
    return wrapper


def personal_workspace(user) -> Workspace:
    return db.session.query(Workspace).filter_by(owner_user_id=user.id, kind="personal").one()


def membership_of(user) -> TeamMembership | None:
    return db.session.query(TeamMembership).filter_by(user_id=user.id).first()


def can_view_image(user, image) -> bool:
    if image.owner_user_id == user.id:
        return True
    if image.visibility == "team":                         # RF-19: solo lo compartido explícitamente
        m = membership_of(user)
        return bool(m and m.team_workspace_id == image.workspace_id)
    return False


def get_image_or_404(image_id):
    image = db.session.get(Image, image_id)
    if not image or not can_view_image(g.user, image):
        abort(404, description="No encontrado.")          # RNF-02: nunca revelar si existe
    return image


def get_job_or_404(job_id):
    job = db.session.get(ProcessingJob, job_id)
    if not job or not (job.requested_by == g.user.id or can_view_image(g.user, job.image)):
        abort(404, description="No encontrado.")
    return job


def get_team_membership_or_404(team_id):
    m = membership_of(g.user)
    if not m or m.team_workspace_id != team_id:
        abort(404, description="No encontrado.")          # CU06 flujo 2a
    return m
```

### 6.4 `backend/app/services/image_service.py`

```python
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models import Image, audit
from ..security.uploads import validate_image
from ..storage.local_private import new_key, save_bytes
from .permission_service import personal_workspace


def image_json(image):
    return {"id": image.id, "filename": image.original_filename, "mime": image.mime_type,
            "width": image.width, "height": image.height, "byte_size": image.byte_size,
            "visibility": image.visibility, "created_at": image.created_at.isoformat()}


def create_image(user, file_storage) -> Image:
    """CU03 pasos 1–2: valida, guarda el original en privado y registra la imagen (RF-06 a RF-08)."""
    info = validate_image(file_storage)                     # lanza UploadError si algo falla
    key = new_key(info["ext"])
    save_bytes("originals", key, info["bytes"])
    image = Image(owner_user_id=user.id, workspace_id=personal_workspace(user).id, original_storage_key=key,
                  original_filename=(secure_filename(file_storage.filename or "") or "imagen")[:255],
                  mime_type=info["mime"], byte_size=len(info["bytes"]),
                  width=info["width"], height=info["height"], source_type="ai_generated")
    db.session.add(image)
    db.session.flush()
    audit(user.id, "image.upload", "image", image.id, mime=info["mime"], byte_size=len(info["bytes"]))
    return image
```

### 6.5 `backend/app/services/job_service.py`

```python
from sqlalchemy.exc import IntegrityError
from flask import current_app
from ..ai.prompts import DEFAULT_SEED, PRESETS
from ..extensions import db
from ..models import ProcessingJob, audit

STATUS_ES = {"queued": "En cola", "processing": "Procesando", "completed": "Completado", "failed": "Error"}
ERROR_ES = {
    "motor_error": "El motor de IA falló al procesar la imagen.",
    "modelo_no_disponible": "El modelo de IA no está instalado o no se pudo cargar.",
    "resultado_inexistente": "El resultado no se guardó correctamente.",
    "contenido_bloqueado": "El filtro de seguridad del modelo bloqueó el resultado.",
    "gpu_memoria": "La GPU se quedó sin memoria. Prueba con una imagen más pequeña.",
}
PUBLIC_PARAMS = ("strength", "steps", "guidance", "seed", "work_size", "seconds", "vram_gb")


def job_json(job, user):
    return {
        "id": job.id, "image_id": job.image_id, "image_filename": job.image.original_filename,
        "status": job.status, "status_label": STATUS_ES[job.status], "preset": job.preset,
        "model_id": job.model_id, "model_version": job.model_version,
        "parameters": {k: v for k, v in (job.parameters or {}).items() if k in PUBLIC_PARAMS},
        "error_code": job.error_code, "error_message": ERROR_ES.get(job.error_code) if job.error_code else None,
        "attempt_count": job.attempt_count, "visibility": job.image.visibility,
        "is_owner": job.image.owner_user_id == user.id,
        "created_at": job.created_at.isoformat(),
        "finished_at": job.finished_at.isoformat() if job.finished_at else None,
    }


def create_job(user, image, preset, idem_key):
    """RF-09: misma clave de idempotencia = mismo trabajo (CU03 flujo 3a)."""
    existing = db.session.query(ProcessingJob).filter_by(requested_by=user.id, idempotency_key=idem_key).first()
    if existing:
        return existing, False
    if current_app.config["AI_ENGINE"] != "local" or preset not in PRESETS:
        preset = "natural"
    params = dict(PRESETS[preset], seed=DEFAULT_SEED)        # RNF-10: parámetros y semilla registrados
    job = ProcessingJob(image_id=image.id, requested_by=user.id, idempotency_key=idem_key,
                        preset=preset, parameters=params, status="queued")
    db.session.add(job)
    try:
        db.session.flush()
    except IntegrityError:                                   # dos solicitudes simultáneas con la misma clave
        db.session.rollback()
        return db.session.query(ProcessingJob).filter_by(requested_by=user.id, idempotency_key=idem_key).one(), False
    audit(user.id, "job.create", "job", job.id, preset=preset)
    return job, True
```

### 6.6 `backend/app/services/team_service.py` (F4: CU05 y CU06)

```python
import hashlib
import secrets
from datetime import timedelta
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from ..extensions import db, utc_now
from ..models import Image, ProcessingJob, TeamInvitation, TeamMembership, User, Workspace, audit
from .permission_service import membership_of, personal_workspace

INVITATION_HOURS = 72


class TeamError(Exception):
    def __init__(self, code, message, status=409):
        super().__init__(message)
        self.code, self.message, self.status = code, message, status


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_team(user, name):
    if membership_of(user):
        raise TeamError("ya_tiene_equipo", "Ya perteneces a un equipo.")             # CU05 flujo 1a
    team = Workspace(name=name, kind="team", owner_user_id=user.id)
    db.session.add(team)
    db.session.flush()
    db.session.add(TeamMembership(team_workspace_id=team.id, user_id=user.id, role="owner"))
    audit(user.id, "team.create", "workspace", team.id)
    return team


def create_invitation(user, team_id):
    m = membership_of(user)
    if not m or m.team_workspace_id != team_id:
        raise TeamError("no_encontrado", "No encontrado.", 404)
    if m.role != "owner":
        raise TeamError("solo_propietario", "Solo el propietario puede invitar.", 403)
    token = secrets.token_urlsafe(32)                                               # se muestra una sola vez
    inv = TeamInvitation(team_workspace_id=team_id, created_by=user.id, token_hash=_hash(token),
                         expires_at=utc_now() + timedelta(hours=INVITATION_HOURS))
    db.session.add(inv)
    db.session.flush()
    audit(user.id, "team.invite", "team_invitation", inv.id)                        # nunca se guarda el token
    return {"link": f"/app/equipo?token={token}", "expires_at": inv.expires_at.isoformat()}


def accept_invitation(user, token):
    inv = db.session.execute(select(TeamInvitation).where(TeamInvitation.token_hash == _hash(token or ""))
                             .with_for_update()).scalar_one_or_none()
    if not inv or inv.used_at is not None or inv.expires_at < utc_now():
        raise TeamError("invitacion_invalida", "La invitación no es válida, ya se usó o venció.", 400)  # CU05 3a
    team = db.session.get(Workspace, inv.team_workspace_id)
    if not team or team.kind != "team":                                             # validación transaccional
        raise TeamError("invitacion_invalida", "La invitación no es válida.", 400)
    if membership_of(user):
        raise TeamError("ya_tiene_equipo", "Ya perteneces a otro equipo.")
    db.session.add(TeamMembership(team_workspace_id=team.id, user_id=user.id, role="member"))
    inv.used_at = utc_now()
    try:
        db.session.flush()
    except IntegrityError:                                                          # UNIQUE(user_id)
        db.session.rollback()
        raise TeamError("ya_tiene_equipo", "Ya perteneces a otro equipo.")
    audit(user.id, "team.join", "workspace", team.id)
    return team


def remove_member(user, team_id, target_user_id):
    m = membership_of(user)
    if not m or m.team_workspace_id != team_id:
        raise TeamError("no_encontrado", "No encontrado.", 404)
    target = db.session.query(TeamMembership).filter_by(team_workspace_id=team_id, user_id=target_user_id).first()
    if not target:
        raise TeamError("no_encontrado", "No encontrado.", 404)
    if target.role == "owner":
        raise TeamError("propietario", "El propietario no puede salir de su propio equipo.")
    if target_user_id != user.id and m.role != "owner":
        raise TeamError("solo_propietario", "Solo el propietario puede retirar integrantes.", 403)
    # Las imágenes que compartió vuelven a ser privadas en su espacio personal
    leaving = db.session.get(User, target_user_id)
    ws = personal_workspace(leaving)
    db.session.query(Image).filter_by(owner_user_id=target_user_id, workspace_id=team_id).update(
        {"workspace_id": ws.id, "visibility": "private"})
    db.session.delete(target)
    audit(user.id, "team.remove_member", "user", target_user_id, team_id=team_id)


def set_visibility(user, image, visibility):
    """RF-19: compartir de forma explícita una imagen con el equipo, o volver a hacerla privada."""
    if visibility == "team":
        m = membership_of(user)
        if not m:
            raise TeamError("sin_equipo", "Primero únete a un equipo.")
        image.workspace_id, image.visibility = m.team_workspace_id, "team"
    else:
        image.workspace_id, image.visibility = personal_workspace(user).id, "private"
    audit(user.id, "image.visibility", "image", image.id, visibility=image.visibility)


def team_stats(team_id, days):
    """RF-20: solo cifras agregadas; nunca rutas ni nombres de imágenes."""
    since = utc_now() - timedelta(days=days)
    members = select(TeamMembership.user_id).where(TeamMembership.team_workspace_id == team_id)
    base = select(ProcessingJob).where(ProcessingJob.requested_by.in_(members), ProcessingJob.created_at >= since)
    q = base.subquery()
    total = db.session.scalar(select(func.count()).select_from(q)) or 0
    completed = db.session.scalar(select(func.count()).select_from(q).where(q.c.status == "completed")) or 0
    failed = db.session.scalar(select(func.count()).select_from(q).where(q.c.status == "failed")) or 0
    avg = db.session.scalar(select(func.avg(func.extract("epoch", q.c.finished_at - q.c.started_at)))
                            .where(q.c.status == "completed"))
    day = func.date_trunc("day", q.c.created_at)
    per_day = db.session.execute(select(day.label("d"), func.count()).group_by("d").order_by("d")).all()
    return {"days": days, "total": total, "completed": completed, "failed": failed,
            "avg_seconds": round(float(avg), 1) if avg is not None else None,
            "per_day": [{"day": d.date().isoformat(), "total": n} for d, n in per_day]}
```

---

## 7. API REST completa (A04–A07)

> Los endpoints son los de la **Tabla E1** del informe. Además se agregan 5 que el código necesita (márcalos en el paso 16 para añadirlos a la Tabla E1): `GET /auth/csrf`, `GET /health`, `PATCH /images/{id}/visibility` (RF-19), `GET /teams/{id}/stats` (RF-20) y `PATCH /admin/incidents/{id}` (CU07 flujo 3a).

### 7.1 `backend/app/api/auth.py` (CU01: RF-01, RF-02, RF-03, RF-17)

```python
import re
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from flask import Blueprint, g, request, session
from flask_wtf.csrf import generate_csrf
from sqlalchemy.exc import IntegrityError
from . import fail, ok
from ..extensions import db, limiter
from ..models import User, Workspace, audit
from ..services.permission_service import login_required

bp = Blueprint("auth", __name__)
ph = PasswordHasher()                      # Argon2id con parámetros recomendados (RNF-01)
DUMMY_HASH = ph.hash("contrasena-de-relleno-para-igualar-tiempos")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD = 12


def user_json(u):
    return {"id": u.id, "email": u.email, "display_name": u.display_name, "role": u.global_role}


def _open_session(user):
    session.clear()
    session.permanent = True
    session["user_id"] = user.id


@bp.get("/auth/csrf")
def csrf_token():
    return ok({"csrf_token": generate_csrf()})


@bp.post("/auth/register")
@limiter.limit("10/hour")
def register():
    d = request.get_json(silent=True) or {}
    email = (d.get("email") or "").strip().lower()
    name = (d.get("display_name") or "").strip()
    password = d.get("password") or ""
    if not EMAIL_RE.match(email) or len(email) > 254 or not (1 <= len(name) <= 120) or len(password) < MIN_PASSWORD:
        return fail("datos_invalidos", f"Revisa el correo, el nombre y una contraseña de al menos {MIN_PASSWORD} caracteres.", 400)
    if db.session.query(User).filter_by(email=email).first():
        return fail("no_disponible", "No se pudo crear la cuenta. Si ya tienes una, inicia sesión.", 409)   # CP-02
    user = User(email=email, display_name=name, password_hash=ph.hash(password))
    db.session.add(user)
    try:
        db.session.flush()
        db.session.add(Workspace(name=f"Espacio de {name}"[:120], kind="personal", owner_user_id=user.id))
        audit(user.id, "user.register", "user", user.id)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return fail("no_disponible", "No se pudo crear la cuenta. Si ya tienes una, inicia sesión.", 409)
    _open_session(user)
    return ok(user_json(user), 201)


@bp.post("/auth/login")
@limiter.limit("5/minute")                 # CU01 excepción: bloqueo temporal ante muchos intentos
def login():
    d = request.get_json(silent=True) or {}
    email = (d.get("email") or "").strip().lower()
    password = d.get("password") or ""
    user = db.session.query(User).filter_by(email=email).first()
    try:
        if not user or not user.is_active:
            ph.verify(DUMMY_HASH, password + "x")            # mismo tiempo de respuesta
            raise VerifyMismatchError
        ph.verify(user.password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return fail("credenciales", "Correo o contraseña incorrectos.", 401)   # mensaje genérico (CP-03)
    if ph.check_needs_rehash(user.password_hash):
        user.password_hash = ph.hash(password)
    audit(user.id, "user.login", "user", user.id)
    db.session.commit()
    _open_session(user)
    return ok(user_json(user))


@bp.post("/auth/logout")
@login_required
def logout():
    audit(g.user.id, "user.logout", "user", g.user.id)
    db.session.commit()
    session.clear()
    return ok({"logged_out": True})


@bp.get("/auth/me")
@login_required
def me():
    return ok(user_json(g.user))
```

**Cómo funciona el CSRF:** el frontend pide `GET /api/v1/auth/csrf` y envía ese valor en la cabecera `X-CSRFToken` en cada `POST`, `PATCH` o `DELETE`. Sin el token, Flask responde **403** (CP-13).

### 7.2 `backend/app/api/users.py` (CU02: RF-04, RF-05 y `GET /workspaces`)

```python
from argon2.exceptions import VerificationError, VerifyMismatchError
from flask import Blueprint, g, request
from . import fail, ok
from .auth import MIN_PASSWORD, ph, user_json
from ..extensions import db
from ..models import Workspace, audit
from ..services.permission_service import login_required, membership_of, personal_workspace

bp = Blueprint("users", __name__)


@bp.patch("/users/me")
@login_required
def edit_profile():
    name = ((request.get_json(silent=True) or {}).get("display_name") or "").strip()
    if not (1 <= len(name) <= 120):
        return fail("nombre_invalido", "El nombre debe tener entre 1 y 120 caracteres.", 400)
    g.user.display_name = name
    audit(g.user.id, "user.update_profile", "user", g.user.id)
    db.session.commit()
    return ok(user_json(g.user))


@bp.post("/users/me/change-password")
@login_required
def change_password():
    d = request.get_json(silent=True) or {}
    try:
        ph.verify(g.user.password_hash, d.get("current_password") or "")
    except (VerifyMismatchError, VerificationError):
        return fail("clave_actual", "La contraseña actual no es correcta.", 400)
    new = d.get("new_password") or ""
    if len(new) < MIN_PASSWORD:
        return fail("clave_corta", f"La nueva contraseña debe tener al menos {MIN_PASSWORD} caracteres.", 400)
    g.user.password_hash = ph.hash(new)
    audit(g.user.id, "user.change_password", "user", g.user.id)
    db.session.commit()
    return ok({"changed": True})


@bp.get("/workspaces")
@login_required
def workspaces():
    ws = personal_workspace(g.user)
    items = [{"id": ws.id, "name": ws.name, "kind": "personal", "role": "owner"}]
    m = membership_of(g.user)
    if m:
        team = db.session.get(Workspace, m.team_workspace_id)
        items.append({"id": team.id, "name": team.name, "kind": "team", "role": m.role})
    return ok(items)
```

### 7.3 `backend/app/api/images.py` (CU03 carga, RF-19 compartir)

```python
from flask import Blueprint, g, request, send_file
from . import fail, ok
from ..extensions import db
from ..security.uploads import UploadError
from ..services.image_service import create_image, image_json
from ..services.permission_service import get_image_or_404, login_required
from ..services.team_service import TeamError, set_visibility
from ..storage.local_private import path_for

bp = Blueprint("images", __name__)


@bp.post("/images")
@login_required
def upload():
    if request.form.get("declaracion_ia") != "true":                                   # RF-07, CP-06
        return fail("sin_declaracion", "Confirma que la imagen es generada por IA y que tienes permiso de uso.", 400)
    file = request.files.get("file")
    if not file:
        return fail("sin_archivo", "Selecciona una imagen.", 400)
    try:
        image = create_image(g.user, file)
    except UploadError as e:
        return fail(e.code, e.message, 400)                                             # CP-05
    db.session.commit()
    return ok(image_json(image), 201)


@bp.get("/images/<int:image_id>")
@login_required
def detail(image_id):
    return ok(image_json(get_image_or_404(image_id)))


@bp.get("/images/<int:image_id>/content")
@login_required
def content(image_id):
    image = get_image_or_404(image_id)
    resp = send_file(path_for("originals", image.original_storage_key), mimetype=image.mime_type)
    resp.headers["Cache-Control"] = "private, no-store"
    return resp


@bp.patch("/images/<int:image_id>/visibility")
@login_required
def visibility(image_id):
    image = get_image_or_404(image_id)
    if image.owner_user_id != g.user.id:
        return fail("no_encontrado", "No encontrado.", 404)
    value = (request.get_json(silent=True) or {}).get("visibility")
    if value not in ("private", "team"):
        return fail("valor_invalido", "La visibilidad debe ser private o team.", 400)
    try:
        set_visibility(g.user, image, value)
    except TeamError as e:
        return fail(e.code, e.message, e.status)
    db.session.commit()
    return ok(image_json(image))
```

### 7.4 `backend/app/api/jobs.py` (CU03 solicitud y CU04: RF-09, RF-11, RF-13 a RF-16)

```python
from flask import Blueprint, abort, g, request, send_file
from sqlalchemy import func, select
from . import fail, ok
from ..extensions import db
from ..models import Image, ProcessingJob, audit
from ..services.job_service import create_job, job_json
from ..services.permission_service import get_image_or_404, get_job_or_404, login_required, membership_of
from ..storage.local_private import path_for

bp = Blueprint("jobs", __name__)
PER_PAGE = 12


@bp.post("/jobs")
@login_required
def request_job():
    d = request.get_json(silent=True) or {}
    key = (request.headers.get("Idempotency-Key") or "").strip()
    if not (8 <= len(key) <= 100):
        return fail("sin_clave", "Falta la clave de idempotencia.", 400)
    try:
        image_id = int(d.get("image_id"))
    except (TypeError, ValueError):
        return fail("datos_invalidos", "Falta la imagen.", 400)
    image = get_image_or_404(image_id)
    job, created = create_job(g.user, image, d.get("preset") or "natural", key)
    db.session.commit()
    return ok(job_json(job, g.user), 201 if created else 200)                          # CP-07


@bp.get("/jobs")
@login_required
def history():
    page = max(1, request.args.get("page", 1, type=int))
    ws_id = request.args.get("workspace_id", type=int)
    q = select(ProcessingJob).join(Image, ProcessingJob.image_id == Image.id)
    if ws_id:                                                                           # trabajos compartidos del equipo
        m = membership_of(g.user)
        if not m or m.team_workspace_id != ws_id:
            abort(404, description="No encontrado.")
        q = q.where(Image.workspace_id == ws_id, Image.visibility == "team")
    else:
        q = q.where(ProcessingJob.requested_by == g.user.id)                             # RF-13: solo los propios
    total = db.session.scalar(select(func.count()).select_from(q.subquery())) or 0
    items = db.session.scalars(q.order_by(ProcessingJob.created_at.desc())
                               .limit(PER_PAGE).offset((page - 1) * PER_PAGE)).all()
    return ok({"items": [job_json(j, g.user) for j in items], "page": page,
               "pages": max(1, -(-total // PER_PAGE)), "total": total})


@bp.get("/jobs/<int:job_id>")
@login_required
def job_detail(job_id):
    return ok(job_json(get_job_or_404(job_id), g.user))


@bp.get("/jobs/<int:job_id>/compare")
@login_required
def compare(job_id):
    job = get_job_or_404(job_id)
    if job.status != "completed":
        return fail("no_completado", "El trabajo aún no está completado.", 409)          # CU04 flujo 3a
    return ok({"original_url": f"/api/v1/images/{job.image_id}/content",
               "result_url": f"/api/v1/jobs/{job.id}/download?inline=1",
               "width": job.image.width, "height": job.image.height})


@bp.get("/jobs/<int:job_id>/download")
@login_required
def download(job_id):
    job = get_job_or_404(job_id)                                                         # CP-11: ajeno = 404
    if job.status != "completed" or not job.result_storage_key:
        return fail("no_completado", "El trabajo aún no está completado.", 409)
    inline = request.args.get("inline") == "1"
    if not inline:
        audit(g.user.id, "job.download", "job", job.id)                                  # RF-17, CP-12
        db.session.commit()
    resp = send_file(path_for("results", job.result_storage_key), mimetype="image/png",
                     as_attachment=not inline, download_name=f"lumia_{job.id}_editado_IA.png")   # RF-16
    resp.headers["Cache-Control"] = "private, no-store"
    return resp
```

### 7.5 `backend/app/api/teams.py` (F4: CU05, CU06 — RF-18 a RF-20)

```python
from flask import Blueprint, g, request
from . import fail, ok
from ..extensions import db
from ..models import TeamMembership, User
from ..services.permission_service import get_team_membership_or_404, login_required
from ..services.team_service import (TeamError, accept_invitation, create_invitation, create_team,
                                     remove_member, team_stats)

bp = Blueprint("teams", __name__)


def _team_error(e: TeamError):
    return fail(e.code, e.message, e.status)


@bp.post("/teams")
@login_required
def new_team():
    name = ((request.get_json(silent=True) or {}).get("name") or "").strip()
    if not (1 <= len(name) <= 120):
        return fail("nombre_invalido", "El nombre del equipo debe tener entre 1 y 120 caracteres.", 400)
    try:
        team = create_team(g.user, name)
    except TeamError as e:
        return _team_error(e)
    db.session.commit()
    return ok({"id": team.id, "name": team.name}, 201)


@bp.get("/teams/<int:team_id>/members")
@login_required
def members(team_id):
    get_team_membership_or_404(team_id)
    rows = (db.session.query(TeamMembership, User).join(User, User.id == TeamMembership.user_id)
            .filter(TeamMembership.team_workspace_id == team_id).order_by(TeamMembership.joined_at).all())
    return ok([{"user_id": u.id, "display_name": u.display_name, "role": m.role,
                "joined_at": m.joined_at.isoformat()} for m, u in rows])


@bp.post("/teams/<int:team_id>/invitations")
@login_required
def invite(team_id):
    try:
        data = create_invitation(g.user, team_id)
    except TeamError as e:
        return _team_error(e)
    db.session.commit()
    return ok(data, 201)


@bp.post("/invitations/accept")
@login_required
def accept():
    token = (request.get_json(silent=True) or {}).get("token") or ""
    try:
        team = accept_invitation(g.user, token)
    except TeamError as e:
        return _team_error(e)
    db.session.commit()
    return ok({"team_id": team.id, "name": team.name})


@bp.delete("/teams/<int:team_id>/members/<int:user_id>")
@login_required
def remove(team_id, user_id):
    try:
        remove_member(g.user, team_id, user_id)
    except TeamError as e:
        return _team_error(e)
    db.session.commit()
    return ok({"removed": user_id})


@bp.get("/teams/<int:team_id>/stats")
@login_required
def stats(team_id):
    get_team_membership_or_404(team_id)
    days = request.args.get("days", 30, type=int)
    if days not in (7, 30, 90):                                     # CU06 flujo 4a: filtro por periodo
        days = 30
    return ok(team_stats(team_id, days))
```

### 7.6 `backend/app/api/admin.py` (F4: CU07 — RF-21)

```python
import time
from datetime import timedelta
from flask import Blueprint, current_app, g, request
from sqlalchemy import func, select, text
from . import fail, ok
from ..extensions import db, utc_now
from ..models import ProcessingJob, ServiceIncident, User, audit
from ..services.permission_service import admin_required

bp = Blueprint("admin", __name__)


@bp.get("/admin/overview")
@admin_required
def overview():
    """Solo métricas técnicas agregadas: nunca imágenes, rutas ni nombres de archivo (RF-21)."""
    db_ok = db.session.execute(text("SELECT 1")).scalar() == 1
    beat = current_app.config["PRIVATE_STORAGE_ROOT"] / "worker.heartbeat"
    worker_age = round(time.time() - beat.stat().st_mtime) if beat.exists() else None
    by_status = dict(db.session.execute(select(ProcessingJob.status, func.count()).group_by(ProcessingJob.status)).all())
    since = utc_now() - timedelta(hours=24)
    avg = db.session.scalar(select(func.avg(func.extract("epoch", ProcessingJob.finished_at - ProcessingJob.started_at)))
                            .where(ProcessingJob.status == "completed", ProcessingJob.finished_at >= since))
    failed_24h = db.session.scalar(select(func.count()).where(ProcessingJob.status == "failed",
                                                             ProcessingJob.finished_at >= since)) or 0
    incidents = db.session.scalars(select(ServiceIncident).where(ServiceIncident.status == "open")
                                   .order_by(ServiceIncident.occurred_at.desc()).limit(50)).all()
    return ok({
        "api": "ok", "database": "ok" if db_ok else "error",
        "worker": {"seconds_since_beat": worker_age, "alive": worker_age is not None and worker_age < 30},
        "engine": current_app.config["AI_ENGINE"],
        "jobs_by_status": {s: by_status.get(s, 0) for s in ("queued", "processing", "completed", "failed")},
        "avg_seconds_24h": round(float(avg), 1) if avg is not None else None,
        "failed_24h": failed_24h,
        "users": db.session.scalar(select(func.count()).select_from(User)) or 0,
        "open_incidents": [{"id": i.id, "service_name": i.service_name, "error_code": i.error_code,
                            "occurred_at": i.occurred_at.isoformat()} for i in incidents],
    })


@bp.patch("/admin/incidents/<int:incident_id>")
@admin_required
def resolve_incident(incident_id):
    inc = db.session.get(ServiceIncident, incident_id)
    if not inc:
        return fail("no_encontrado", "No encontrado.", 404)
    if (request.get_json(silent=True) or {}).get("status") != "resolved":
        return fail("valor_invalido", "Solo se puede marcar como resolved.", 400)
    inc.status, inc.resolved_at = "resolved", utc_now()
    audit(g.user.id, "incident.resolve", "service_incident", inc.id)            # CU07 flujo 3a
    db.session.commit()
    return ok({"id": inc.id, "status": inc.status})
```

### 7.7 Primera prueba del backend

```powershell
cd C:\proyectos\lumia-ai\backend; .\.venv\Scripts\Activate.ps1
python -m flask --app wsgi run --port 5000
# en otra ventana:
curl.exe http://localhost:5000/api/v1/health
```

Debe responder `{"data":{"status":"ok","engine":"mock",...},"error":null}`. Antes de esto debes haber creado el paquete `app/ai/` (paso 8), porque `health` importa `app.ai.prompts`. Si quieres probar ya, crea primero el archivo del paso 8.2.

---

## 8. Motor de IA (F3 — A08–A09)

> Skill §8: la humanización necesita una **edición image-to-image controlada**, no restauración facial ni superresolución. El informe propone Stable Diffusion 1.5 img2img con Diffusers como candidato. Se confirma o se cambia con la evaluación del paso 13.

### 8.1 `backend/app/ai/interface.py` (interfaz del skill y MockEngine)

```python
from abc import ABC, abstractmethod
from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngInfo


class EngineError(Exception):
    """Error del motor con un código seguro para el usuario (RF-12)."""
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class HumanizationEngine(ABC):
    model_id: str = ""
    model_version: str = ""

    @abstractmethod
    def humanize(self, input_path: str, output_path: str, preset: str, seed: int | None = None) -> dict:
        """Devuelve metadatos del procesamiento; falla explícitamente ante error."""


def save_labeled(img: Image.Image, output_path: str, source_info: dict) -> None:
    """RF-16: rotula el resultado como editado con IA y conserva los metadatos de procedencia del original."""
    meta = PngInfo()
    for key, value in source_info.items():
        if isinstance(value, str) and key not in ("LUMIA-AI", "Software"):
            meta.add_text(key, value)                   # no se borran metadatos de procedencia (skill §9)
    meta.add_text("LUMIA-AI", "editado con IA")
    meta.add_text("Software", "LUMIA AI")
    kwargs = {"pnginfo": meta}
    if source_info.get("exif"):
        kwargs["exif"] = source_info["exif"]
    img.save(output_path, "PNG", **kwargs)


class MockEngine(HumanizationEngine):
    """SOLO para probar el circuito subida → cola → descarga. Simulación, sin IA real."""
    model_id, model_version = "mock", "simulacion-sin-ia-real"

    def humanize(self, input_path, output_path, preset, seed=None):
        src = Image.open(input_path)
        info = dict(src.info)
        img = src.convert("RGB")
        ImageDraw.Draw(img).text((10, 10), "SIMULACION - SIN IA REAL", fill=(255, 0, 0))
        save_labeled(img, output_path, info)
        return {"model_id": self.model_id, "model_version": self.model_version, "simulated": True}
```

### 8.2 `backend/app/ai/prompts.py` (Anexo D)

```python
POSITIVE = ("Photorealistic natural human appearance, authentic subtle skin microtexture and pores, realistic fine "
            "hair strands, coherent eyes and catchlights, believable lighting and shadows, natural facial detail, "
            "preserve the original person's apparent identity, pose, expression, skin tone, hairstyle, clothing, "
            "framing and background, avoid beauty retouching, documentary photographic realism.")

NEGATIVE = ("plastic skin, airbrushed skin, waxy face, uncanny eyes, oversmoothing, exaggerated pores, distorted "
            "anatomy, extra fingers, altered identity, different skin tone, excessive sharpening, halos, artifacts, "
            "cartoon, CGI look.")

# Anexo D: fuerza 0,20–0,40 · pasos 25–35 · guía 5–7. Si la evaluación (paso 13) muestra que los tres
# presets no se diferencian, deja solo "natural": la interfaz mostrará un único botón (skill §1.4).
PRESETS = {
    "natural":       {"strength": 0.30, "steps": 30, "guidance": 6.0},
    "fotografico":   {"strength": 0.36, "steps": 32, "guidance": 6.5},
    "detalle_suave": {"strength": 0.22, "steps": 28, "guidance": 5.5},
}
DEFAULT_SEED = 1234          # semilla fija registrada (RNF-10)
WORK_SIDE = 640              # lado menor de trabajo, entre 512 y 768 px
```

### 8.3 `backend/app/ai/local_engine.py` (motor real)

```python
import time
import diffusers
import torch
from diffusers import StableDiffusionImg2ImgPipeline
from PIL import Image, ImageOps
from .interface import EngineError, HumanizationEngine, save_labeled
from .prompts import DEFAULT_SEED, NEGATIVE, POSITIVE, PRESETS, WORK_SIDE


class LocalHumanizationEngine(HumanizationEngine):
    def __init__(self, model_path: str, model_id: str):
        self.model_id = model_id or "stable-diffusion-v1-5"
        self.model_version = f"diffusers-{diffusers.__version__}"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        try:
            self.pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
                model_path, torch_dtype=dtype, variant="fp16", use_safetensors=True, local_files_only=True)
        except Exception as e:                                    # pesos ausentes o dañados (CP-09)
            raise EngineError("modelo_no_disponible") from e
        self.pipe = self.pipe.to(self.device)
        self.pipe.enable_attention_slicing()                       # menos VRAM (6 GB)
        self.pipe.set_progress_bar_config(disable=True)

    def humanize(self, input_path, output_path, preset, seed=None):
        p = PRESETS.get(preset, PRESETS["natural"])
        seed = DEFAULT_SEED if seed is None else int(seed)
        src = ImageOps.exif_transpose(Image.open(input_path))
        info = dict(src.info)
        src = src.convert("RGB")
        w, h = src.size
        k = WORK_SIDE / min(w, h)
        work_size = (max(64, int(w * k) // 8 * 8), max(64, int(h * k) // 8 * 8))
        work = src.resize(work_size, Image.LANCZOS)
        generator = torch.Generator(device=self.device).manual_seed(seed)
        if self.device == "cuda":
            torch.cuda.reset_peak_memory_stats()
        t0 = time.perf_counter()
        try:
            res = self.pipe(prompt=POSITIVE, negative_prompt=NEGATIVE, image=work,
                            strength=p["strength"], guidance_scale=p["guidance"],
                            num_inference_steps=p["steps"], generator=generator)
        except torch.cuda.OutOfMemoryError as e:
            raise EngineError("gpu_memoria") from e
        if any(getattr(res, "nsfw_content_detected", None) or []):
            raise EngineError("contenido_bloqueado")
        out = res.images[0].resize((w, h), Image.LANCZOS)          # vuelve al tamaño original
        save_labeled(out, output_path, info)
        vram = torch.cuda.max_memory_allocated() / 1e9 if self.device == "cuda" else 0.0
        return {"model_id": self.model_id, "model_version": self.model_version, "preset": preset,
                **p, "seed": seed, "work_size": list(work_size), "device": self.device,
                "seconds": round(time.perf_counter() - t0, 2), "vram_gb": round(vram, 2)}
```

> Se deja activo el **filtro de seguridad** del modelo (*safety checker*). Si bloquea un retrato normal por error, el trabajo termina con `contenido_bloqueado`; anótalo en la evaluación.

### 8.4 `backend/app/ai/evaluation.py`

El código está en el **paso 13**, porque se usa al evaluar.

### 8.5 Instalar PyTorch, Diffusers y los pesos

**1) PyTorch con CUDA.** Revisa el comando exacto en https://pytorch.org/get-started/locally/ (Windows · Pip · Python · CUDA). Por ejemplo:

```powershell
cd C:\proyectos\lumia-ai\backend; .\.venv\Scripts\Activate.ps1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

Debe imprimir `True` y el nombre de tu GPU.

**2) Diffusers y el resto:**

```powershell
pip install -e ".[ia]"
pip show diffusers transformers torch | Select-String "Name|Version"
```

📌 **Anota las versiones exactas**: la de Diffusers va en la referencia APA del informe (von Platen et al., 2022) y en `docs/motor-ia.md`.

**3) Pesos del modelo** (skill §8: licencia de código **y** de pesos):

1. Abre https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5 y lee su licencia (CreativeML OpenRAIL-M). Anota la fecha, el nombre exacto del repositorio y la licencia.
2. Descarga solo los archivos fp16 (unos 2,5 GB):

```powershell
cd C:\proyectos\lumia-ai
pip install -U "huggingface_hub[cli]"
huggingface-cli download stable-diffusion-v1-5/stable-diffusion-v1-5 `
  --include "*.json" "*.txt" "*.fp16.safetensors" `
  --local-dir .\models\stable-diffusion-v1-5
```

> En versiones nuevas de `huggingface_hub`, el comando se llama `hf download` y usa los mismos parámetros. Si te pide iniciar sesión, usa `huggingface-cli login`.

**4) Prueba directa del motor** con una de tus muestras:

```powershell
cd C:\proyectos\lumia-ai\backend
python -c "from app.ai.local_engine import LocalHumanizationEngine as E; e=E(r'..\models\stable-diffusion-v1-5','stable-diffusion-v1-5'); print(e.humanize(r'C:\lumia_muestras\M01.png', r'C:\lumia_muestras\M01_prueba.png', 'natural'))"
```

Abre `M01_prueba.png` y compáralo con el original. Si la persona cambia demasiado, baja `strength`; si casi no cambia, súbelo (sin pasar de 0,40).

**5)** Cuando funcione, cambia en `.env`: `AI_ENGINE=local`.

---

## 9. Worker (A07)

### `backend/app/workers/image_worker.py`

```python
"""Worker de LUMIA AI: toma trabajos de la cola en PostgreSQL sin duplicados (RF-10)."""
import logging
import signal
import sys
import time
from sqlalchemy import text
from app import create_app
from app.ai.interface import EngineError, MockEngine
from app.extensions import db, utc_now
from app.models import ProcessingJob, ServiceIncident
from app.storage.local_private import new_key, path_for

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("worker")
POLL_SECONDS = 2
STALE_MINUTES = 15
running = True

CLAIM_SQL = text("""
UPDATE processing_jobs
   SET status = 'processing', started_at = now(), attempt_count = attempt_count + 1, error_code = NULL
 WHERE id = (SELECT id FROM processing_jobs
              WHERE status = 'queued'
              ORDER BY created_at
              FOR UPDATE SKIP LOCKED
              LIMIT 1)
RETURNING id
""")

# RNF-08: si el worker se cayó a mitad de un trabajo, al reiniciar ese trabajo vuelve a la cola
RECOVER_SQL = text(f"""
UPDATE processing_jobs SET status = 'queued'
 WHERE status = 'processing' AND started_at < now() - interval '{STALE_MINUTES} minutes'
""")


def build_engine(app):
    if app.config["AI_ENGINE"] != "local":
        log.warning("AI_ENGINE=%s: SIMULACIÓN, SIN IA REAL", app.config["AI_ENGINE"])
        return MockEngine()
    try:
        from app.ai.local_engine import LocalHumanizationEngine
        engine = LocalHumanizationEngine(str(app.config["AI_MODEL_PATH"]), app.config["AI_MODEL_ID"])
        log.info("Motor local cargado: %s (%s) en %s", engine.model_id, engine.model_version, engine.device)
        return engine
    except Exception:                                                        # noqa: BLE001
        log.exception("No se pudo cargar el motor local")
        db.session.add(ServiceIncident(service_name="worker", error_code="modelo_no_disponible"))
        db.session.commit()
        return None                                                          # los trabajos fallarán con código seguro


def heartbeat(app):
    (app.config["PRIVATE_STORAGE_ROOT"] / "worker.heartbeat").write_text(utc_now().isoformat())


def process_one(app, engine) -> bool:
    row = db.session.execute(CLAIM_SQL).first()
    db.session.commit()
    if not row:
        return False
    job = db.session.get(ProcessingJob, row.id)
    key = new_key("png")
    dst = path_for("results", key)
    try:
        if engine is None:
            raise EngineError("modelo_no_disponible")
        src = path_for("originals", job.image.original_storage_key)
        meta = engine.humanize(str(src), str(dst), job.preset, seed=(job.parameters or {}).get("seed"))
        if not dst.is_file() or dst.stat().st_size == 0:                     # RNF-07
            raise EngineError("resultado_inexistente")
        job.result_storage_key = key
        job.model_id, job.model_version = meta.get("model_id"), meta.get("model_version")
        job.parameters = {**(job.parameters or {}),
                          **{k: meta[k] for k in ("seconds", "vram_gb", "work_size", "device") if k in meta}}
        job.status, job.error_code, job.finished_at = "completed", None, utc_now()
        log.info("Trabajo %s completado en %s s", job.id, meta.get("seconds"))
    except Exception as e:                                                   # noqa: BLE001
        code = e.code if isinstance(e, EngineError) else "motor_error"
        log.error("Trabajo %s falló (intento %s): %s", job.id, job.attempt_count, code)
        dst.unlink(missing_ok=True)
        job.error_code = code
        if job.attempt_count < app.config["AI_MAX_ATTEMPTS"]:
            job.status = "queued"                                            # CU03 flujo 4a: se reencola
        else:
            job.status, job.finished_at = "failed", utc_now()                # CU03 flujo 4b
            db.session.add(ServiceIncident(service_name="worker", error_code=code))
    db.session.commit()
    return True


def _stop(*_):
    global running
    running = False


def main():
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    app = create_app()
    with app.app_context():
        db.session.execute(RECOVER_SQL)
        db.session.commit()
        engine = build_engine(app)
        log.info("Worker listo (motor: %s)", app.config["AI_ENGINE"])
        while running:
            heartbeat(app)
            try:
                if not process_one(app, engine):
                    time.sleep(POLL_SECONDS)
            except Exception:                                                # noqa: BLE001 (BD caída, etc.)
                log.exception("Error del ciclo del worker; reintento en 5 s")
                db.session.rollback()
                time.sleep(5)
    sys.exit(0)


if __name__ == "__main__":
    main()
```

Ejecútalo desde `backend/`:

```powershell
python -m app.workers.image_worker
```

---

## 10. Frontend React + TypeScript + Tailwind + shadcn/ui (A04, A07)

### 10.1 Crear el proyecto e instalar dependencias

```powershell
cd C:\proyectos\lumia-ai
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install react-router-dom @tanstack/react-query tailwindcss @tailwindcss/vite
npm install @fontsource-variable/inter @fontsource-variable/fraunces
npm install -D @types/node vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event @playwright/test
```

### 10.2 `frontend/vite.config.ts`

```ts
/// <reference types="vitest/config" />
import path from "path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
  server: { proxy: { "/api": "http://localhost:5000" } },   // mismo origen: las cookies funcionan
  test: { environment: "jsdom", globals: true, setupFiles: "./src/tests/setup.ts", include: ["src/**/*.test.{ts,tsx}"] },
});
```

En **`tsconfig.json`** y en **`tsconfig.app.json`**, agrega dentro de `"compilerOptions"`:

```json
"baseUrl": ".",
"paths": { "@/*": ["./src/*"] }
```

### 10.3 Estilos y shadcn/ui

1. Crea **`src/styles/globals.css`** con esta línea y borra `src/index.css` y `src/App.css`:

```css
@import "tailwindcss";
```

2. Inicializa shadcn/ui. Cuando te pregunte por el archivo CSS, elige `src/styles/globals.css`:

```powershell
npx shadcn@latest init
npx shadcn@latest add button card input label checkbox tabs dialog tooltip dropdown-menu sonner progress badge table select
```

3. **Al final** de `src/styles/globals.css` (después de lo que agregó shadcn), pega la identidad tipográfica y la accesibilidad:

```css
@import "@fontsource-variable/inter";
@import "@fontsource-variable/fraunces";

@theme {
  --font-sans: "Inter Variable", system-ui, sans-serif;
  --font-display: "Fraunces Variable", Georgia, serif;
}

:focus-visible { outline: 2px solid currentColor; outline-offset: 2px; }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; scroll-behavior: auto !important; }
}
```

> Skill §7: la paleta definitiva se elige **después** de probar prototipos. shadcn crea variables de color (`--primary`, `--background`, etc.) en `globals.css`: prueba 2 o 3 combinaciones, verifica el contraste AA (RNF-04) con las DevTools de Chrome y quédate con una. Las fuentes se instalan como paquetes, así que no se necesita Internet en la demostración.

Borra `src/App.tsx`: no se usa.

### 10.4 `src/lib/types.ts`

```ts
export type User = { id: number; email: string; display_name: string; role: "user" | "admin" };
export type JobStatus = "queued" | "processing" | "completed" | "failed";
export type Job = {
  id: number; image_id: number; image_filename: string; status: JobStatus; status_label: string;
  preset: string; model_id: string | null; model_version: string | null;
  parameters: Record<string, unknown>; error_code: string | null; error_message: string | null;
  attempt_count: number; visibility: "private" | "team"; is_owner: boolean;
  created_at: string; finished_at: string | null;
};
export type JobPage = { items: Job[]; page: number; pages: number; total: number };
export type ImageInfo = { id: number; filename: string; width: number; height: number; visibility: "private" | "team" };
export type Workspace = { id: number; name: string; kind: "personal" | "team"; role: "owner" | "member" };
export type Member = { user_id: number; display_name: string; role: "owner" | "member"; joined_at: string };
export type TeamStats = {
  days: number; total: number; completed: number; failed: number; avg_seconds: number | null;
  per_day: { day: string; total: number }[];
};
export type Health = { status: string; engine: "local" | "mock"; presets: string[] };
export type Overview = {
  api: string; database: string; engine: string;
  worker: { seconds_since_beat: number | null; alive: boolean };
  jobs_by_status: Record<JobStatus, number>; avg_seconds_24h: number | null; failed_24h: number; users: number;
  open_incidents: { id: number; service_name: string; error_code: string; occurred_at: string }[];
};
```

### 10.5 `src/lib/api.ts`

```ts
type Envelope<T> = { data: T | null; error: { code: string; message: string } | null };

export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string) { super(message); }
}

let csrfToken: string | null = null;
export const resetCsrf = () => { csrfToken = null; };

async function getCsrf(): Promise<string> {
  if (!csrfToken) {
    const r = await fetch("/api/v1/auth/csrf", { credentials: "include" });
    const j = (await r.json()) as Envelope<{ csrf_token: string }>;
    csrfToken = j.data!.csrf_token;
  }
  return csrfToken;
}

export async function api<T>(path: string, opts: RequestInit = {}, retry = true): Promise<T> {
  const method = (opts.method ?? "GET").toUpperCase();
  const headers = new Headers(opts.headers);
  if (method !== "GET") headers.set("X-CSRFToken", await getCsrf());
  if (opts.body && !(opts.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const r = await fetch(`/api/v1${path}`, { ...opts, method, headers, credentials: "include" });
  let j: Envelope<T> | null = null;
  try { j = (await r.json()) as Envelope<T>; } catch { /* respuesta sin JSON */ }
  if (r.status === 403 && j?.error?.code === "csrf" && retry) {   // token renovado tras iniciar sesión
    resetCsrf();
    return api<T>(path, opts, false);
  }
  if (!r.ok || j?.error) {
    throw new ApiError(r.status, j?.error?.code ?? "error", j?.error?.message ?? "No se pudo conectar con el servidor.");
  }
  return j!.data as T;
}
```

### 10.6 Hooks por funcionalidad (`src/features/`)

**`src/features/auth/useAuth.ts`**

```ts
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, resetCsrf } from "@/lib/api";
import type { User } from "@/lib/types";

export const useMe = () =>
  useQuery({ queryKey: ["me"], queryFn: () => api<User>("/auth/me"), retry: false, staleTime: 60_000 });

export function useLogin() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (b: { email: string; password: string }) => api<User>("/auth/login", { method: "POST", body: JSON.stringify(b) }),
    onSuccess: (u) => { resetCsrf(); qc.setQueryData(["me"], u); },
  });
}

export function useRegister() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (b: { email: string; display_name: string; password: string }) =>
      api<User>("/auth/register", { method: "POST", body: JSON.stringify(b) }),
    onSuccess: (u) => { resetCsrf(); qc.setQueryData(["me"], u); },
  });
}

export function useLogout() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api("/auth/logout", { method: "POST" }),
    onSettled: () => { resetCsrf(); qc.clear(); },
  });
}

export function useUpdateProfile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (display_name: string) => api<User>("/users/me", { method: "PATCH", body: JSON.stringify({ display_name }) }),
    onSuccess: (u) => qc.setQueryData(["me"], u),
  });
}

export const useChangePassword = () =>
  useMutation({
    mutationFn: (b: { current_password: string; new_password: string }) =>
      api("/users/me/change-password", { method: "POST", body: JSON.stringify(b) }),
  });
```

**`src/features/images/useImages.ts`**

```ts
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ImageInfo } from "@/lib/types";

export const useUploadImage = () =>
  useMutation({
    mutationFn: (file: File) => {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("declaracion_ia", "true");
      return api<ImageInfo>("/images", { method: "POST", body: fd });
    },
  });

export function useSetVisibility() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (b: { imageId: number; visibility: "private" | "team" }) =>
      api<ImageInfo>(`/images/${b.imageId}/visibility`, { method: "PATCH", body: JSON.stringify({ visibility: b.visibility }) }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["job"] }); qc.invalidateQueries({ queryKey: ["jobs"] }); },
  });
}
```

**`src/features/jobs/useJobs.ts`**

```ts
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Health, Job, JobPage } from "@/lib/types";

export const useHealth = () => useQuery({ queryKey: ["health"], queryFn: () => api<Health>("/health"), staleTime: 30_000 });

export const useJobs = (page: number, workspaceId?: number) =>
  useQuery({
    queryKey: ["jobs", page, workspaceId ?? "mine"],
    queryFn: () => api<JobPage>(`/jobs?page=${page}${workspaceId ? `&workspace_id=${workspaceId}` : ""}`),
  });

export const useJob = (id: number) =>
  useQuery({
    queryKey: ["job", id],
    queryFn: () => api<Job>(`/jobs/${id}`),
    refetchInterval: (q) => {
      const s = q.state.data?.status;
      return s === "queued" || s === "processing" ? 2000 : false;      // consulta hasta un estado final
    },
  });

export function useCreateJob() {
  const qc = useQueryClient();
  return useMutation({
    // La clave de idempotencia la crea la página una vez por intención (RF-09)
    mutationFn: (b: { image_id: number; preset: string; key: string }) =>
      api<Job>("/jobs", { method: "POST", headers: { "Idempotency-Key": b.key },
                          body: JSON.stringify({ image_id: b.image_id, preset: b.preset }) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["jobs"] }),
  });
}
```

**`src/features/teams/useTeams.ts`**

```ts
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Member, Overview, TeamStats, Workspace } from "@/lib/types";

export const useWorkspaces = () => useQuery({ queryKey: ["workspaces"], queryFn: () => api<Workspace[]>("/workspaces") });

export const useMembers = (teamId?: number) =>
  useQuery({ queryKey: ["members", teamId], queryFn: () => api<Member[]>(`/teams/${teamId}/members`), enabled: !!teamId });

export const useTeamStats = (teamId: number | undefined, days: number) =>
  useQuery({ queryKey: ["stats", teamId, days], queryFn: () => api<TeamStats>(`/teams/${teamId}/stats?days=${days}`), enabled: !!teamId });

function useInvalidateTeam() {
  const qc = useQueryClient();
  return () => ["workspaces", "members", "stats", "jobs"].forEach((k) => qc.invalidateQueries({ queryKey: [k] }));
}

export function useCreateTeam() {
  const inv = useInvalidateTeam();
  return useMutation({ mutationFn: (name: string) => api("/teams", { method: "POST", body: JSON.stringify({ name }) }), onSuccess: inv });
}

export const useInvite = () =>
  useMutation({ mutationFn: (teamId: number) => api<{ link: string; expires_at: string }>(`/teams/${teamId}/invitations`, { method: "POST" }) });

export function useAcceptInvite() {
  const inv = useInvalidateTeam();
  return useMutation({ mutationFn: (token: string) => api("/invitations/accept", { method: "POST", body: JSON.stringify({ token }) }), onSuccess: inv });
}

export function useRemoveMember() {
  const inv = useInvalidateTeam();
  return useMutation({
    mutationFn: (b: { teamId: number; userId: number }) => api(`/teams/${b.teamId}/members/${b.userId}`, { method: "DELETE" }),
    onSuccess: inv,
  });
}

export const useOverview = () =>
  useQuery({ queryKey: ["overview"], queryFn: () => api<Overview>("/admin/overview"), refetchInterval: 10_000, retry: false });

export function useResolveIncident() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api(`/admin/incidents/${id}`, { method: "PATCH", body: JSON.stringify({ status: "resolved" }) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["overview"] }),
  });
}
```

### 10.7 Componentes

**`src/components/StatusBadge.tsx`**

```tsx
import { Badge } from "@/components/ui/badge";
import type { JobStatus } from "@/lib/types";

const LABEL: Record<JobStatus, string> = { queued: "En cola", processing: "Procesando", completed: "Completado", failed: "Error" };
const VARIANT: Record<JobStatus, "secondary" | "default" | "outline" | "destructive"> =
  { queued: "secondary", processing: "outline", completed: "default", failed: "destructive" };

export function StatusBadge({ status }: { status: JobStatus }) {
  return <Badge variant={VARIANT[status]}>{LABEL[status]}</Badge>;
}
```

**`src/components/ImageUploader.tsx`**

```tsx
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { useUploadImage } from "@/features/images/useImages";
import type { ImageInfo } from "@/lib/types";

const TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX_MB = 10;

export function ImageUploader({ onUploaded }: { onUploaded: (img: ImageInfo, previewUrl: string) => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>("");
  const [declared, setDeclared] = useState(false);
  const [localError, setLocalError] = useState("");
  const upload = useUploadImage();

  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview); }, [preview]);

  function pick(f: File | null) {
    setLocalError("");
    if (!f) return;
    if (!TYPES.includes(f.type)) return setLocalError("Solo se aceptan imágenes JPG, PNG o WebP.");
    if (f.size > MAX_MB * 1024 * 1024) return setLocalError(`El archivo supera ${MAX_MB} MB.`);
    setFile(f);
    setPreview(URL.createObjectURL(f));
  }

  const error = localError || (upload.error as Error | null)?.message;

  return (
    <div className="space-y-4">
      <label
        className="flex min-h-72 cursor-pointer flex-col items-center justify-center gap-2 rounded-2xl border-2 border-dashed p-6 text-center transition-colors hover:bg-muted/50 focus-within:ring-2"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => { e.preventDefault(); pick(e.dataTransfer.files[0] ?? null); }}
      >
        {preview ? (
          <img src={preview} alt="Vista previa de la imagen seleccionada" className="max-h-96 rounded-xl object-contain" />
        ) : (
          <>
            <span className="font-medium">Arrastra tu imagen generada por IA o haz clic para elegirla</span>
            <span className="text-sm text-muted-foreground">JPG · PNG · WebP · hasta {MAX_MB} MB</span>
          </>
        )}
        <input type="file" accept={TYPES.join(",")} className="sr-only" aria-label="Seleccionar imagen"
               onChange={(e) => pick(e.target.files?.[0] ?? null)} />
      </label>
      <div className="flex items-start gap-2">
        <Checkbox id="declaracion" checked={declared} onCheckedChange={(v) => setDeclared(v === true)} />
        <Label htmlFor="declaracion" className="text-sm leading-snug">
          Confirmo que la imagen es generada por IA y que tengo permiso para usarla
        </Label>
      </div>
      {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
      <Button disabled={!file || !declared || upload.isPending}
              onClick={() => file && upload.mutate(file, { onSuccess: (img) => onUploaded(img, preview) })}>
        {upload.isPending ? "Subiendo…" : "Subir imagen"}
      </Button>
    </div>
  );
}
```

**`src/components/JobProgress.tsx`**

```tsx
import { useEffect } from "react";
import { Progress } from "@/components/ui/progress";
import { useJob } from "@/features/jobs/useJobs";
import type { Job } from "@/lib/types";

const STEP = { queued: 25, processing: 65, completed: 100, failed: 100 } as const;

export function JobProgress({ jobId, onDone }: { jobId: number; onDone?: (j: Job) => void }) {
  const { data } = useJob(jobId);
  useEffect(() => {
    if (data && (data.status === "completed" || data.status === "failed")) onDone?.(data);
  }, [data?.status]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="space-y-2" aria-live="polite">
      <div className="flex justify-between text-sm">
        <span className="font-medium">{data?.status_label ?? "En cola"}</span>
        {data && data.attempt_count > 1 && <span className="text-muted-foreground">Intento {data.attempt_count}</span>}
      </div>
      <Progress value={STEP[data?.status ?? "queued"]} aria-label="Progreso del trabajo" />
    </div>
  );
}
```

**`src/components/BeforeAfterSlider.tsx`** (manejable con mouse, toque y teclado)

```tsx
import { useState } from "react";

export function BeforeAfterSlider({ before, after }: { before: string; after: string }) {
  const [pos, setPos] = useState(50);
  return (
    <figure className="space-y-2">
      <div className="relative w-full select-none overflow-hidden rounded-2xl bg-muted">
        <img src={after} alt="Resultado editado con IA" className="block w-full" draggable={false} />
        <img src={before} alt="Imagen original" draggable={false}
             className="absolute inset-0 h-full w-full object-cover"
             style={{ clipPath: `inset(0 ${100 - pos}% 0 0)` }} />
        <div aria-hidden className="pointer-events-none absolute inset-y-0 w-0.5 bg-white shadow-[0_0_8px_rgba(0,0,0,.5)]"
             style={{ left: `${pos}%` }} />
        <span className="absolute left-3 top-3 rounded-md bg-black/60 px-2 py-0.5 text-xs text-white">Antes</span>
        <span className="absolute right-3 top-3 rounded-md bg-black/60 px-2 py-0.5 text-xs text-white">Después · editado con IA</span>
        <input type="range" min={0} max={100} value={pos} aria-label="Comparar antes y después"
               onChange={(e) => setPos(Number(e.target.value))}
               className="absolute inset-0 h-full w-full cursor-ew-resize opacity-0" />
      </div>
      <figcaption className="text-xs text-muted-foreground">Desliza o usa las flechas del teclado para comparar.</figcaption>
    </figure>
  );
}
```

### 10.8 Layouts

**`src/app/layouts/PublicLayout.tsx`**

```tsx
import { Link, Outlet } from "react-router-dom";
import { Button } from "@/components/ui/button";

export default function PublicLayout() {
  return (
    <div className="min-h-screen bg-background font-sans text-foreground">
      <a href="#contenido" className="sr-only focus:not-sr-only focus:absolute focus:p-2">Saltar al contenido</a>
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <Link to="/" className="font-display text-xl font-semibold tracking-tight">LUMIA AI</Link>
        <nav className="flex gap-2">
          <Button variant="ghost" asChild><Link to="/login">Ingresar</Link></Button>
          <Button asChild><Link to="/registro">Crear cuenta</Link></Button>
        </nav>
      </header>
      <main id="contenido"><Outlet /></main>
      <footer className="mx-auto max-w-6xl px-6 py-10 text-sm text-muted-foreground">
        LUMIA AI procesa las imágenes en esta computadora. Los resultados se identifican como editados con IA.
      </footer>
    </div>
  );
}
```

**`src/app/layouts/AppLayout.tsx`** (protege todas las rutas `/app`)

```tsx
import { Navigate, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useLogout, useMe } from "@/features/auth/useAuth";

const LINKS = [
  { to: "/app", label: "Panel", end: true },
  { to: "/app/humanizar", label: "Humanizar" },
  { to: "/app/historial", label: "Historial" },
  { to: "/app/equipo", label: "Equipo" },
  { to: "/app/perfil", label: "Perfil" },
];

export default function AppLayout() {
  const { data: me, isLoading, isError } = useMe();
  const logout = useLogout();
  const nav = useNavigate();
  const location = useLocation();

  if (isLoading) return <p className="p-10" aria-live="polite">Cargando…</p>;
  if (isError || !me) return <Navigate to="/login" replace state={{ from: location.pathname }} />;

  const links = me.role === "admin" ? [...LINKS, { to: "/app/admin", label: "Admin" }] : LINKS;
  return (
    <div className="min-h-screen bg-background font-sans text-foreground">
      <a href="#contenido" className="sr-only focus:not-sr-only focus:absolute focus:p-2">Saltar al contenido</a>
      <header className="border-b">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-4 px-6 py-3">
          <span className="font-display text-lg font-semibold">LUMIA AI</span>
          <nav className="flex flex-1 flex-wrap gap-1" aria-label="Principal">
            {links.map((l) => (
              <NavLink key={l.to} to={l.to} end={l.end}
                       className={({ isActive }) => `rounded-md px-3 py-1.5 text-sm ${isActive ? "bg-muted font-medium" : "hover:bg-muted/60"}`}>
                {l.label}
              </NavLink>
            ))}
          </nav>
          <span className="text-sm text-muted-foreground">{me.display_name}</span>
          <Button variant="outline" size="sm" onClick={() => logout.mutate(undefined, { onSettled: () => nav("/") })}>Salir</Button>
        </div>
      </header>
      <main id="contenido" className="mx-auto max-w-6xl px-6 py-8"><Outlet /></main>
    </div>
  );
}
```

### 10.9 Rutas — `src/app/router.tsx` (rutas del skill §7)

```tsx
import { createBrowserRouter } from "react-router-dom";
import PublicLayout from "./layouts/PublicLayout";
import AppLayout from "./layouts/AppLayout";
import Home from "@/pages/Home";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import Dashboard from "@/pages/Dashboard";
import Humanize from "@/pages/Humanize";
import History from "@/pages/History";
import JobDetail from "@/pages/JobDetail";
import Profile from "@/pages/Profile";
import Team from "@/pages/Team";
import Admin from "@/pages/Admin";

export const router = createBrowserRouter([
  {
    element: <PublicLayout />,
    children: [
      { path: "/", element: <Home /> },
      { path: "/login", element: <Login /> },
      { path: "/registro", element: <Register /> },
    ],
  },
  {
    path: "/app",
    element: <AppLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "humanizar", element: <Humanize /> },
      { path: "historial", element: <History /> },
      { path: "trabajos/:id", element: <JobDetail /> },
      { path: "perfil", element: <Profile /> },
      { path: "equipo", element: <Team /> },
      { path: "admin", element: <Admin /> },
    ],
  },
]);
```

### 10.10 `src/main.tsx`

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/sonner";
import { router } from "@/app/router";
import "@/styles/globals.css";

const queryClient = new QueryClient({ defaultOptions: { queries: { refetchOnWindowFocus: false } } });

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <Toaster richColors position="top-right" />
    </QueryClientProvider>
  </React.StrictMode>
);
```

En **`frontend/index.html`** cambia `<html lang="en">` por `<html lang="es">` y el `<title>` por `LUMIA AI`.

### 10.11 Páginas

**`src/pages/Home.tsx`** (landing pública, skill §7 y criterio de aceptación 1)

```tsx
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { BeforeAfterSlider } from "@/components/BeforeAfterSlider";

// Cambia a true SOLO cuando tengas un par antes/después REAL y autorizado (paso 13) en public/demo/
const DEMO_REAL = false;

const PASOS = [
  { n: "01", t: "Sube tu imagen", d: "Un retrato de persona generado por IA, en JPG, PNG o WebP de hasta 10 MB." },
  { n: "02", t: "Humaniza", d: "El motor local ajusta piel, ojos, cabello y luz con una edición de baja intensidad." },
  { n: "03", t: "Compara y descarga", d: "Desliza para ver el antes y el después; el resultado se rotula «editado con IA»." },
];

const FAQ = [
  ["¿Mi imagen sale de esta computadora?", "No. El procesamiento es local y las imágenes se guardan en un almacén privado, fuera de rutas públicas."],
  ["¿El resultado deja de ser una imagen de IA?", "No. LUMIA AI aumenta el realismo visual percibido; el resultado sigue siendo una imagen editada con IA y se identifica así."],
  ["¿Cambia el rostro de la persona?", "Busca conservar la identidad aparente, la pose, el tono de piel, la ropa y el fondo. Puede haber cambios leves; por eso siempre conservas el original."],
  ["¿Repara manos y cuerpos completos?", "Es una función experimental: solo se anuncia si las pruebas lo confirman."],
];

export default function Home() {
  return (
    <div className="mx-auto max-w-6xl px-6">
      <section className="grid items-center gap-10 py-16 md:grid-cols-2 md:py-24">
        <div className="space-y-6">
          <p className="text-sm font-medium uppercase tracking-widest text-muted-foreground">Humanización visual con IA local</p>
          <h1 className="font-display text-4xl font-semibold leading-tight md:text-6xl">De imagen generada a apariencia más natural</h1>
          <p className="max-w-prose text-lg text-muted-foreground">
            LUMIA AI edita retratos de personas creados con inteligencia artificial para que se vean más fotográficos:
            piel con textura real, ojos coherentes, cabello y luz creíbles. Sin embellecer y sin cambiar a la persona.
          </p>
          <div className="flex flex-wrap gap-3">
            <Button size="lg" asChild><Link to="/registro">Empezar</Link></Button>
            <Button size="lg" variant="outline" asChild><a href="#como-funciona">Cómo funciona</a></Button>
          </div>
        </div>
        {DEMO_REAL ? (
          <div className="space-y-2">
            <BeforeAfterSlider before="/demo/antes.jpg" after="/demo/despues.png" />
            <p className="text-xs text-muted-foreground">Resultado real de LUMIA AI con una imagen autorizada.</p>
          </div>
        ) : (
          <Card className="aspect-[4/5] overflow-hidden">
            <CardContent className="flex h-full flex-col justify-end bg-gradient-to-br from-muted to-background p-6">
              <p className="font-display text-2xl">Antes · Después</p>
              <p className="text-sm text-muted-foreground">Ilustración de concepto. Los ejemplos reales se publican después de la evaluación.</p>
            </CardContent>
          </Card>
        )}
      </section>

      <section id="como-funciona" className="py-16">
        <h2 className="font-display text-3xl font-semibold">Tres pasos</h2>
        <div className="mt-8 grid gap-6 md:grid-cols-3">
          {PASOS.map((p) => (
            <Card key={p.n}><CardContent className="space-y-2 p-6">
              <span className="font-display text-3xl text-muted-foreground">{p.n}</span>
              <h3 className="text-lg font-semibold">{p.t}</h3>
              <p className="text-muted-foreground">{p.d}</p>
            </CardContent></Card>
          ))}
        </div>
      </section>

      <section className="grid gap-10 py-16 md:grid-cols-2">
        <div>
          <h2 className="font-display text-3xl font-semibold">Beneficios, con sus límites</h2>
          <ul className="mt-6 space-y-3 text-muted-foreground">
            <li>✔ Menos regeneraciones y retoque manual de retratos sintéticos.</li>
            <li>✔ El original nunca se modifica y siempre puedes compararlo.</li>
            <li>✔ Procesamiento local: tus imágenes no se envían a terceros.</li>
            <li>✖ No convierte una imagen sintética en una foto de una persona real.</li>
            <li>✖ No garantiza reparar manos ni anatomía.</li>
          </ul>
        </div>
        <div>
          <h2 className="font-display text-3xl font-semibold">Privacidad</h2>
          <p className="mt-6 text-muted-foreground">
            Solo tú ves tus imágenes, salvo que decidas compartir una con tu equipo. El administrador técnico ve métricas
            agregadas, nunca tus fotos. Los resultados conservan los metadatos de procedencia y se rotulan «editado con IA».
          </p>
        </div>
      </section>

      <section className="py-16">
        <h2 className="font-display text-3xl font-semibold">Preguntas frecuentes</h2>
        <div className="mt-6 divide-y rounded-2xl border">
          {FAQ.map(([q, a]) => (
            <details key={q} className="group p-5">
              <summary className="cursor-pointer font-medium">{q}</summary>
              <p className="mt-2 text-muted-foreground">{a}</p>
            </details>
          ))}
        </div>
      </section>

      <section className="py-16 text-center">
        <h2 className="font-display text-3xl font-semibold">Prueba LUMIA AI con tu primera imagen</h2>
        <Button size="lg" className="mt-6" asChild><Link to="/registro">Crear cuenta</Link></Button>
      </section>
    </div>
  );
}
```

**`src/pages/Login.tsx`**

```tsx
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLogin } from "@/features/auth/useAuth";

export default function Login() {
  const nav = useNavigate();
  const from = (useLocation().state as { from?: string } | null)?.from ?? "/app";
  const login = useLogin();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  return (
    <Card className="mx-auto my-16 max-w-sm">
      <CardHeader><CardTitle className="font-display text-2xl">Iniciar sesión</CardTitle></CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); login.mutate({ email, password }, { onSuccess: () => nav(from, { replace: true }) }); }}>
          <div className="space-y-1"><Label htmlFor="email">Correo</Label>
            <Input id="email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></div>
          <div className="space-y-1"><Label htmlFor="password">Contraseña</Label>
            <Input id="password" type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} /></div>
          {login.error && <p role="alert" className="text-sm text-destructive">{(login.error as Error).message}</p>}
          <Button type="submit" className="w-full" disabled={login.isPending}>{login.isPending ? "Entrando…" : "Entrar"}</Button>
          <p className="text-center text-sm">¿No tienes cuenta? <Link className="underline" to="/registro">Regístrate</Link></p>
        </form>
      </CardContent>
    </Card>
  );
}
```

**`src/pages/Register.tsx`**

```tsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useRegister } from "@/features/auth/useAuth";

export default function Register() {
  const nav = useNavigate();
  const reg = useRegister();
  const [f, setF] = useState({ display_name: "", email: "", password: "" });
  const set = (k: keyof typeof f) => (e: React.ChangeEvent<HTMLInputElement>) => setF({ ...f, [k]: e.target.value });

  return (
    <Card className="mx-auto my-16 max-w-sm">
      <CardHeader><CardTitle className="font-display text-2xl">Crear cuenta</CardTitle></CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); reg.mutate(f, { onSuccess: () => nav("/app", { replace: true }) }); }}>
          <div className="space-y-1"><Label htmlFor="name">Nombre</Label>
            <Input id="name" required maxLength={120} value={f.display_name} onChange={set("display_name")} /></div>
          <div className="space-y-1"><Label htmlFor="email">Correo</Label>
            <Input id="email" type="email" autoComplete="email" required value={f.email} onChange={set("email")} /></div>
          <div className="space-y-1"><Label htmlFor="password">Contraseña (mínimo 12 caracteres)</Label>
            <Input id="password" type="password" autoComplete="new-password" required minLength={12} value={f.password} onChange={set("password")} /></div>
          {reg.error && <p role="alert" className="text-sm text-destructive">{(reg.error as Error).message}</p>}
          <Button type="submit" className="w-full" disabled={reg.isPending}>{reg.isPending ? "Creando…" : "Crear cuenta"}</Button>
          <p className="text-center text-sm">¿Ya tienes cuenta? <Link className="underline" to="/login">Inicia sesión</Link></p>
        </form>
      </CardContent>
    </Card>
  );
}
```

**`src/pages/Dashboard.tsx`** (`/app`)

```tsx
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/StatusBadge";
import { useMe } from "@/features/auth/useAuth";
import { useHealth, useJobs } from "@/features/jobs/useJobs";

export default function Dashboard() {
  const { data: me } = useMe();
  const { data: health } = useHealth();
  const { data: jobs } = useJobs(1);
  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-semibold">Hola, {me?.display_name}</h1>
          <p className="text-muted-foreground">Tienes {jobs?.total ?? 0} trabajos de humanización.</p>
        </div>
        <Button size="lg" asChild><Link to="/app/humanizar">Humanizar una imagen</Link></Button>
      </div>
      {health?.engine === "mock" && (
        <p role="status" className="rounded-lg border border-amber-500 bg-amber-50 p-3 text-sm text-amber-900">
          Modo simulación: el motor de IA real no está activo. Los resultados NO son humanización real.
        </p>
      )}
      <Card>
        <CardHeader><CardTitle>Últimos trabajos</CardTitle></CardHeader>
        <CardContent>
          {jobs?.items.length ? (
            <ul className="divide-y">
              {jobs.items.slice(0, 5).map((j) => (
                <li key={j.id} className="flex items-center justify-between py-3">
                  <Link className="underline-offset-4 hover:underline" to={`/app/trabajos/${j.id}`}>{j.image_filename}</Link>
                  <StatusBadge status={j.status} />
                </li>
              ))}
            </ul>
          ) : <p className="text-muted-foreground">Aún no tienes trabajos. Sube tu primera imagen.</p>}
        </CardContent>
      </Card>
    </div>
  );
}
```

**`src/pages/Humanize.tsx`** (Estudio)

```tsx
import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ImageUploader } from "@/components/ImageUploader";
import { JobProgress } from "@/components/JobProgress";
import { BeforeAfterSlider } from "@/components/BeforeAfterSlider";
import { useCreateJob, useHealth } from "@/features/jobs/useJobs";
import type { ImageInfo, Job } from "@/lib/types";

const PRESET_LABEL: Record<string, string> = { natural: "Natural", fotografico: "Fotográfico", detalle_suave: "Detalle suave" };

export default function Humanize() {
  const { data: health } = useHealth();
  const createJob = useCreateJob();
  const [image, setImage] = useState<ImageInfo | null>(null);
  const [preview, setPreview] = useState("");
  const [preset, setPreset] = useState("natural");
  const [key, setKey] = useState("");                 // una clave por intención de humanizar
  const [jobId, setJobId] = useState<number | null>(null);
  const [done, setDone] = useState<Job | null>(null);
  const presets = health?.presets ?? [];

  function humanize() {
    if (!image) return;
    const k = key || crypto.randomUUID();
    setKey(k);
    createJob.mutate({ image_id: image.id, preset, key: k }, { onSuccess: (j) => { setJobId(j.id); setDone(null); } });
  }

  function reset() { setImage(null); setPreview(""); setJobId(null); setDone(null); setKey(""); }

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      <section className="space-y-5">
        <h1 className="font-display text-3xl font-semibold">Estudio de humanización</h1>
        {health?.engine === "mock" && (
          <p role="status" className="rounded-lg border border-amber-500 bg-amber-50 p-3 text-sm text-amber-900">Simulación, sin IA real.</p>
        )}
        {!image ? (
          <ImageUploader onUploaded={(img, url) => { setImage(img); setPreview(url); }} />
        ) : (
          <div className="space-y-4">
            <img src={preview} alt="Imagen original subida" className="max-h-96 w-full rounded-2xl object-contain" />
            {presets.length > 1 && (
              <Tabs value={preset} onValueChange={(v) => { setPreset(v); setKey(""); }}>
                <TabsList>{presets.map((p) => <TabsTrigger key={p} value={p}>{PRESET_LABEL[p] ?? p}</TabsTrigger>)}</TabsList>
              </Tabs>
            )}
            <div className="flex flex-wrap gap-3">
              <Button size="lg" onClick={humanize} disabled={createJob.isPending || (!!jobId && !done)}>Humanizar imagen</Button>
              <Button variant="outline" onClick={reset}>Usar otra imagen</Button>
            </div>
            {createJob.error && <p role="alert" className="text-sm text-destructive">{(createJob.error as Error).message}</p>}
            {jobId && !done && <JobProgress jobId={jobId} onDone={setDone} />}
            {done?.status === "failed" && (
              <p role="alert" className="text-sm text-destructive">
                {done.error_message ?? "No se pudo procesar."} <button className="underline" onClick={() => { setKey(""); setDone(null); setJobId(null); }}>Reintentar</button>
              </p>
            )}
          </div>
        )}
      </section>
      <section>
        {done?.status === "completed" ? (
          <div className="space-y-4">
            <BeforeAfterSlider before={`/api/v1/images/${done.image_id}/content`} after={`/api/v1/jobs/${done.id}/download?inline=1`} />
            <div className="flex flex-wrap gap-3">
              <Button asChild><a href={`/api/v1/jobs/${done.id}/download`}>Descargar resultado</a></Button>
              <Button variant="outline" asChild><Link to={`/app/trabajos/${done.id}`}>Ver detalle</Link></Button>
            </div>
          </div>
        ) : (
          <div className="flex h-full min-h-72 items-center justify-center rounded-2xl border p-6 text-center text-muted-foreground">
            Aquí verás la comparación antes y después.
          </div>
        )}
      </section>
    </div>
  );
}
```

**`src/pages/History.tsx`**

```tsx
import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/StatusBadge";
import { useJobs } from "@/features/jobs/useJobs";
import { useWorkspaces } from "@/features/teams/useTeams";

export default function History() {
  const [page, setPage] = useState(1);
  const [ws, setWs] = useState<number | undefined>(undefined);
  const { data: workspaces } = useWorkspaces();
  const team = workspaces?.find((w) => w.kind === "team");
  const { data, isLoading } = useJobs(page, ws);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-display text-3xl font-semibold">Historial</h1>
        {team && (
          <label className="text-sm">Ver:{" "}
            <select className="rounded-md border bg-background px-2 py-1" value={ws ?? ""}
                    onChange={(e) => { setPage(1); setWs(e.target.value ? Number(e.target.value) : undefined); }}>
              <option value="">Mis trabajos</option>
              <option value={team.id}>Compartidos en {team.name}</option>
            </select>
          </label>
        )}
      </div>
      {isLoading ? <p>Cargando…</p> : data?.items.length ? (
        <div className="overflow-x-auto rounded-2xl border">
          <table className="w-full text-sm">
            <thead className="bg-muted/50 text-left"><tr>
              <th className="p-3">Imagen</th><th className="p-3">Estado</th><th className="p-3">Preset</th><th className="p-3">Fecha</th>
            </tr></thead>
            <tbody>
              {data.items.map((j) => (
                <tr key={j.id} className="border-t">
                  <td className="p-3"><Link className="underline-offset-4 hover:underline" to={`/app/trabajos/${j.id}`}>{j.image_filename}</Link></td>
                  <td className="p-3"><StatusBadge status={j.status} /></td>
                  <td className="p-3">{j.preset}</td>
                  <td className="p-3">{new Date(j.created_at).toLocaleString("es-PE")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : <p className="text-muted-foreground">No hay trabajos todavía.</p>}
      {data && data.pages > 1 && (
        <div className="flex items-center gap-3">
          <Button variant="outline" disabled={page <= 1} onClick={() => setPage(page - 1)}>Anterior</Button>
          <span className="text-sm">Página {data.page} de {data.pages}</span>
          <Button variant="outline" disabled={page >= data.pages} onClick={() => setPage(page + 1)}>Siguiente</Button>
        </div>
      )}
    </div>
  );
}
```

**`src/pages/JobDetail.tsx`**

```tsx
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BeforeAfterSlider } from "@/components/BeforeAfterSlider";
import { JobProgress } from "@/components/JobProgress";
import { StatusBadge } from "@/components/StatusBadge";
import { useCreateJob, useJob } from "@/features/jobs/useJobs";
import { useSetVisibility } from "@/features/images/useImages";
import { useWorkspaces } from "@/features/teams/useTeams";

export default function JobDetail() {
  const id = Number(useParams().id);
  const nav = useNavigate();
  const { data: job, isError } = useJob(id);
  const retry = useCreateJob();
  const share = useSetVisibility();
  const { data: workspaces } = useWorkspaces();
  const inTeam = workspaces?.some((w) => w.kind === "team");

  if (isError) return <p>No encontrado.</p>;
  if (!job) return <p>Cargando…</p>;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="font-display text-3xl font-semibold">{job.image_filename}</h1>
        <StatusBadge status={job.status} />
        {job.model_id === "mock" && <span className="text-sm text-amber-700">Simulación, sin IA real</span>}
      </div>
      {(job.status === "queued" || job.status === "processing") && <JobProgress jobId={job.id} />}
      {job.status === "completed" && (
        <BeforeAfterSlider before={`/api/v1/images/${job.image_id}/content`} after={`/api/v1/jobs/${job.id}/download?inline=1`} />
      )}
      {job.status === "failed" && <p role="alert" className="text-destructive">{job.error_message}</p>}
      <div className="flex flex-wrap gap-3">
        {job.status === "completed" && <Button asChild><a href={`/api/v1/jobs/${job.id}/download`}>Descargar resultado</a></Button>}
        {job.is_owner && job.status !== "queued" && job.status !== "processing" && (
          <Button variant="outline" disabled={retry.isPending}
                  onClick={() => retry.mutate({ image_id: job.image_id, preset: job.preset, key: crypto.randomUUID() },
                                              { onSuccess: (j) => nav(`/app/trabajos/${j.id}`) })}>
            {job.status === "failed" ? "Reintentar" : "Procesar de nuevo"}
          </Button>
        )}
        {job.is_owner && inTeam && (
          <Button variant="outline" disabled={share.isPending}
                  onClick={() => share.mutate({ imageId: job.image_id, visibility: job.visibility === "team" ? "private" : "team" },
                                              { onSuccess: () => toast.success("Visibilidad actualizada") })}>
            {job.visibility === "team" ? "Dejar de compartir con el equipo" : "Compartir con mi equipo"}
          </Button>
        )}
      </div>
      <Card>
        <CardHeader><CardTitle>Trazabilidad</CardTitle></CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 gap-2 text-sm md:grid-cols-4">
            <dt className="text-muted-foreground">Modelo</dt><dd>{job.model_id ?? "—"}</dd>
            <dt className="text-muted-foreground">Versión</dt><dd>{job.model_version ?? "—"}</dd>
            <dt className="text-muted-foreground">Preset</dt><dd>{job.preset}</dd>
            <dt className="text-muted-foreground">Intentos</dt><dd>{job.attempt_count}</dd>
            {Object.entries(job.parameters).map(([k, v]) => (
              <div key={k} className="contents"><dt className="text-muted-foreground">{k}</dt><dd>{String(v)}</dd></div>
            ))}
          </dl>
        </CardContent>
      </Card>
    </div>
  );
}
```

**`src/pages/Profile.tsx`**

```tsx
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useChangePassword, useMe, useUpdateProfile } from "@/features/auth/useAuth";

export default function Profile() {
  const { data: me } = useMe();
  const update = useUpdateProfile();
  const change = useChangePassword();
  const [name, setName] = useState(me?.display_name ?? "");
  const [pw, setPw] = useState({ current_password: "", new_password: "" });

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader><CardTitle>Perfil</CardTitle></CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); update.mutate(name, { onSuccess: () => toast.success("Perfil actualizado") }); }}>
            <p className="text-sm text-muted-foreground">{me?.email}</p>
            <div className="space-y-1"><Label htmlFor="name">Nombre visible</Label>
              <Input id="name" required maxLength={120} value={name} onChange={(e) => setName(e.target.value)} /></div>
            {update.error && <p role="alert" className="text-sm text-destructive">{(update.error as Error).message}</p>}
            <Button type="submit" disabled={update.isPending}>Guardar</Button>
          </form>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>Cambiar contraseña</CardTitle></CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); change.mutate(pw, { onSuccess: () => { toast.success("Contraseña cambiada"); setPw({ current_password: "", new_password: "" }); } }); }}>
            <div className="space-y-1"><Label htmlFor="cur">Contraseña actual</Label>
              <Input id="cur" type="password" autoComplete="current-password" required value={pw.current_password} onChange={(e) => setPw({ ...pw, current_password: e.target.value })} /></div>
            <div className="space-y-1"><Label htmlFor="new">Nueva contraseña (mínimo 12)</Label>
              <Input id="new" type="password" autoComplete="new-password" required minLength={12} value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} /></div>
            {change.error && <p role="alert" className="text-sm text-destructive">{(change.error as Error).message}</p>}
            <Button type="submit" disabled={change.isPending}>Cambiar</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
```

**`src/pages/Team.tsx`** (F4: CU05 y CU06)

```tsx
import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useMe } from "@/features/auth/useAuth";
import { useAcceptInvite, useCreateTeam, useInvite, useMembers, useRemoveMember, useTeamStats, useWorkspaces } from "@/features/teams/useTeams";

export default function Team() {
  const [params, setParams] = useSearchParams();
  const token = params.get("token");
  const { data: me } = useMe();
  const { data: workspaces } = useWorkspaces();
  const team = workspaces?.find((w) => w.kind === "team");
  const [name, setName] = useState("");
  const [days, setDays] = useState(30);
  const [link, setLink] = useState("");
  const create = useCreateTeam();
  const accept = useAcceptInvite();
  const invite = useInvite();
  const remove = useRemoveMember();
  const { data: members } = useMembers(team?.id);
  const { data: stats } = useTeamStats(team?.id, days);

  useEffect(() => {
    if (token && workspaces && !team && !accept.isPending && !accept.isSuccess && !accept.isError) {
      accept.mutate(token, { onSuccess: () => { toast.success("Te uniste al equipo"); setParams({}); } });
    }
  }, [token, workspaces, team]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!team) {
    return (
      <Card className="max-w-md">
        <CardHeader><CardTitle>Equipo</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          {accept.error && <p role="alert" className="text-sm text-destructive">{(accept.error as Error).message}</p>}
          <p className="text-muted-foreground">No perteneces a un equipo. Crea uno o abre el enlace de invitación que te enviaron.</p>
          <form className="space-y-3" onSubmit={(e) => { e.preventDefault(); create.mutate(name); }}>
            <Label htmlFor="team">Nombre del equipo</Label>
            <Input id="team" required maxLength={120} value={name} onChange={(e) => setName(e.target.value)} />
            {create.error && <p role="alert" className="text-sm text-destructive">{(create.error as Error).message}</p>}
            <Button type="submit" disabled={create.isPending}>Crear equipo</Button>
          </form>
        </CardContent>
      </Card>
    );
  }

  const isOwner = team.role === "owner";
  const max = Math.max(1, ...(stats?.per_day.map((d) => d.total) ?? [1]));

  return (
    <div className="space-y-6">
      <h1 className="font-display text-3xl font-semibold">{team.name}</h1>
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Integrantes</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <ul className="divide-y">
              {members?.map((m) => (
                <li key={m.user_id} className="flex items-center justify-between py-2">
                  <span>{m.display_name} <span className="text-xs text-muted-foreground">({m.role === "owner" ? "propietario" : "integrante"})</span></span>
                  {m.role !== "owner" && (isOwner || m.user_id === me?.id) && (
                    <Button size="sm" variant="ghost" onClick={() => remove.mutate({ teamId: team.id, userId: m.user_id })}>
                      {m.user_id === me?.id ? "Salir" : "Retirar"}
                    </Button>
                  )}
                </li>
              ))}
            </ul>
            {isOwner && (
              <div className="space-y-2">
                <Button variant="outline" onClick={() => invite.mutate(team.id, { onSuccess: (d) => setLink(window.location.origin + d.link) })}>Generar invitación</Button>
                {link && (
                  <div className="space-y-1">
                    <Input readOnly value={link} aria-label="Enlace de invitación" onFocus={(e) => e.target.select()} />
                    <p className="text-xs text-muted-foreground">Un solo uso, vence en 72 horas. Cópialo ahora: no se vuelve a mostrar.</p>
                  </div>
                )}
              </div>
            )}
            <Link className="text-sm underline" to="/app/historial">Ver imágenes compartidas en el historial</Link>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Estadísticas</CardTitle>
            <select aria-label="Periodo" className="rounded-md border bg-background px-2 py-1 text-sm" value={days} onChange={(e) => setDays(Number(e.target.value))}>
              <option value={7}>7 días</option><option value={30}>30 días</option><option value={90}>90 días</option>
            </select>
          </CardHeader>
          <CardContent className="space-y-4">
            <dl className="grid grid-cols-2 gap-3 text-sm">
              <div><dt className="text-muted-foreground">Trabajos</dt><dd className="text-2xl font-semibold">{stats?.total ?? 0}</dd></div>
              <div><dt className="text-muted-foreground">Completados</dt><dd className="text-2xl font-semibold">{stats?.completed ?? 0}</dd></div>
              <div><dt className="text-muted-foreground">Fallidos</dt><dd className="text-2xl font-semibold">{stats?.failed ?? 0}</dd></div>
              <div><dt className="text-muted-foreground">Tiempo medio</dt><dd className="text-2xl font-semibold">{stats?.avg_seconds != null ? `${stats.avg_seconds} s` : "—"}</dd></div>
            </dl>
            <div className="flex h-32 items-end gap-1" role="img" aria-label="Trabajos por día">
              {stats?.per_day.map((d) => (
                <div key={d.day} title={`${d.day}: ${d.total}`} className="flex-1 rounded-t bg-primary" style={{ height: `${(d.total / max) * 100}%` }} />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

**`src/pages/Admin.tsx`** (F4: CU07)

```tsx
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useOverview, useResolveIncident } from "@/features/teams/useTeams";

export default function Admin() {
  const { data, error } = useOverview();
  const resolve = useResolveIncident();
  if (error) return <p role="alert">{(error as Error).message}</p>;
  if (!data) return <p>Cargando…</p>;
  const cards = [
    ["API", data.api], ["Base de datos", data.database],
    ["Worker", data.worker.alive ? `activo (${data.worker.seconds_since_beat} s)` : "sin señal"], ["Motor", data.engine],
    ["En cola", data.jobs_by_status.queued], ["Procesando", data.jobs_by_status.processing],
    ["Completados", data.jobs_by_status.completed], ["Fallidos", data.jobs_by_status.failed],
    ["Tiempo medio 24 h", data.avg_seconds_24h != null ? `${data.avg_seconds_24h} s` : "—"], ["Usuarios", data.users],
  ];
  return (
    <div className="space-y-6">
      <h1 className="font-display text-3xl font-semibold">Supervisión técnica</h1>
      <p className="text-sm text-muted-foreground">Solo métricas agregadas. Esta vista no muestra imágenes de los usuarios.</p>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
        {cards.map(([k, v]) => (
          <Card key={String(k)}><CardContent className="p-4"><p className="text-xs text-muted-foreground">{k}</p><p className="text-lg font-semibold">{String(v)}</p></CardContent></Card>
        ))}
      </div>
      <Card>
        <CardHeader><CardTitle>Incidentes abiertos</CardTitle></CardHeader>
        <CardContent>
          {data.open_incidents.length ? (
            <ul className="divide-y">
              {data.open_incidents.map((i) => (
                <li key={i.id} className="flex items-center justify-between py-2 text-sm">
                  <span>{new Date(i.occurred_at).toLocaleString("es-PE")} · {i.service_name} · {i.error_code}</span>
                  <Button size="sm" variant="outline" onClick={() => resolve.mutate(i.id)}>Marcar resuelto</Button>
                </li>
              ))}
            </ul>
          ) : <p className="text-muted-foreground">Sin incidentes abiertos.</p>}
        </CardContent>
      </Card>
    </div>
  );
}
```

### 10.12 Ejecutar en modo desarrollo

Abre tres ventanas de PowerShell:

```powershell
# 1) API
cd C:\proyectos\lumia-ai\backend; .\.venv\Scripts\Activate.ps1; python -m flask --app wsgi run --port 5000
# 2) Worker
cd C:\proyectos\lumia-ai\backend; .\.venv\Scripts\Activate.ps1; python -m app.workers.image_worker
# 3) Frontend
cd C:\proyectos\lumia-ai\frontend; npm run dev        # abre http://localhost:5173
```

Recorre el sistema completo: registro → panel → humanizar → historial → detalle → descarga → perfil → equipo. Para el panel de administración, registra tu usuario y luego ejecuta:

```powershell
cd C:\proyectos\lumia-ai\backend; .\.venv\Scripts\Activate.ps1
python -m flask --app wsgi crear-admin tu_correo@ejemplo.com
```

**Modo demostración** (un solo servidor, como en la sustentación): `npm run build` en `frontend/`; después solo hacen falta la API y el worker. Flask sirve la web en http://localhost:5000 (esto lo automatiza `iniciar.ps1`).

---

## 11. Pruebas automatizadas: pytest, Vitest y Playwright (A10)

### 11.1 `backend/tests/conftest.py`

```python
import io
import os
import pytest
from PIL import Image as PILImage
from app import create_app
from app.extensions import db


def url_bd_pruebas():
    return os.environ["DATABASE_URL"].rsplit("/", 1)[0] + "/lumia_test"     # base separada (paso 3)


@pytest.fixture()
def app(tmp_path):
    app = create_app(TESTING=True, WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False, AI_ENGINE="mock",
                     SQLALCHEMY_DATABASE_URI=url_bd_pruebas(), PRIVATE_STORAGE_ROOT=tmp_path)
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def other_client(app):
    return app.test_client()


def image_bytes(fmt="PNG", size=(64, 64)):
    buf = io.BytesIO()
    PILImage.new("RGB", size, (200, 150, 120)).save(buf, fmt)
    buf.seek(0)
    return buf


def register(client, email="a@demo.pe", name="Demo"):
    return client.post("/api/v1/auth/register", json={"email": email, "display_name": name, "password": "clave-segura-123"})


def upload(client, fmt="PNG", name="a.png", size=(64, 64)):
    r = client.post("/api/v1/images", data={"file": (image_bytes(fmt, size), name), "declaracion_ia": "true"},
                    content_type="multipart/form-data")
    return r


def new_job(client, image_id, key="clave-prueba-0001"):
    return client.post("/api/v1/jobs", json={"image_id": image_id}, headers={"Idempotency-Key": key})
```

### 11.2 `backend/tests/test_auth.py` (CP-01, CP-02, CP-03, CP-13, RF-03, RNF-01)

```python
from argon2 import PasswordHasher
from app import create_app
from app.extensions import db
from app.models import User, Workspace
from tests.conftest import register, url_bd_pruebas


def test_cp01_registro_valido(client):
    r = register(client)
    assert r.status_code == 201
    user = db.session.query(User).filter_by(email="a@demo.pe").one()
    assert db.session.query(Workspace).filter_by(owner_user_id=user.id, kind="personal").count() == 1
    assert user.password_hash.startswith("$argon2id$")                       # RNF-01: sin contraseñas en claro
    assert client.get("/api/v1/auth/me").status_code == 200                   # sesión abierta


def test_cp02_correo_existente(client, other_client):
    register(client)
    r = register(other_client)
    assert r.status_code == 409
    assert db.session.query(User).count() == 1


def test_cp03_login_invalido(client, other_client):
    register(client)
    r = other_client.post("/api/v1/auth/login", json={"email": "a@demo.pe", "password": "incorrecta-123"})
    assert r.status_code == 401
    assert r.json["error"]["message"] == "Correo o contraseña incorrectos."
    assert other_client.get("/api/v1/auth/me").status_code == 401


def test_rf03_logout(client):
    register(client)
    assert client.post("/api/v1/auth/logout").status_code == 200
    assert client.get("/api/v1/auth/me").status_code == 401


def test_cp13_csrf(tmp_path):
    app = create_app(TESTING=True, RATELIMIT_ENABLED=False, SQLALCHEMY_DATABASE_URI=url_bd_pruebas(), PRIVATE_STORAGE_ROOT=tmp_path)
    r = app.test_client().post("/api/v1/auth/login", json={"email": "x@demo.pe", "password": "x"})
    assert r.status_code == 403
    assert r.json["error"]["code"] == "csrf"


def test_rnf01_limite_de_intentos(tmp_path):
    app = create_app(TESTING=True, WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=True,
                     SQLALCHEMY_DATABASE_URI=url_bd_pruebas(), PRIVATE_STORAGE_ROOT=tmp_path)
    with app.app_context():
        db.create_all()
        c = app.test_client()
        codes = [c.post("/api/v1/auth/login", json={"email": "x@demo.pe", "password": "x"}).status_code for _ in range(6)]
        db.drop_all()
    assert codes[-1] == 429


def test_rf05_cambio_de_clave(client):
    register(client)
    bad = client.post("/api/v1/users/me/change-password", json={"current_password": "otra", "new_password": "nueva-clave-456"})
    assert bad.status_code == 400
    ok = client.post("/api/v1/users/me/change-password", json={"current_password": "clave-segura-123", "new_password": "nueva-clave-456"})
    assert ok.status_code == 200
```

### 11.3 `backend/tests/test_imagenes.py` (CP-04, CP-05, CP-06, RF-06, RF-08)

```python
import io
from app.extensions import db
from app.models import Image
from tests.conftest import image_bytes, register, upload


def test_cp04_carga_jpg_valida(client, app):
    register(client)
    r = upload(client, fmt="JPEG", name="retrato.jpg", size=(800, 1000))
    assert r.status_code == 201
    img = db.session.get(Image, r.json["data"]["id"])
    path = app.config["PRIVATE_STORAGE_ROOT"] / "originals" / img.original_storage_key
    assert path.is_file()                                                      # almacén privado
    assert "retrato" not in img.original_storage_key                           # nombre aleatorio


def test_cp05_extension_falsa(client):
    register(client)
    fake = io.BytesIO(b"MZ\x90\x00" + b"\x00" * 400)                          # cabecera de un .exe
    r = client.post("/api/v1/images", data={"file": (fake, "virus.png"), "declaracion_ia": "true"},
                    content_type="multipart/form-data")
    assert r.status_code == 400
    assert r.json["error"]["code"] == "imagen_invalida"


def test_cp06_sin_declaracion(client):
    register(client)
    r = client.post("/api/v1/images", data={"file": (image_bytes(), "a.png")}, content_type="multipart/form-data")
    assert r.status_code == 400
    assert r.json["error"]["code"] == "sin_declaracion"


def test_rf06_demasiados_pixeles(client):
    register(client)
    r = upload(client, size=(5000, 5000))                                      # 25 MP > 24 MP
    assert r.status_code == 400
    assert r.json["error"]["code"] == "demasiados_pixeles"


def test_rf08_sin_ruta_publica(client):
    register(client)
    img = db.session.get(Image, upload(client).json["data"]["id"])
    r = client.get(f"/private_data/originals/{img.original_storage_key}")
    assert r.mimetype != "image/png"                                         # nunca se sirve el archivo
```

### 11.4 `backend/tests/test_trabajos.py` (CP-07, CP-08, CP-09, CP-11, CP-12, RNF-07)

```python
from app.ai.interface import HumanizationEngine, MockEngine
from app.extensions import db
from app.models import AuditEvent, ProcessingJob, ServiceIncident
from app.workers.image_worker import CLAIM_SQL, process_one
from tests.conftest import new_job, register, upload


def _job(client):
    register(client)
    image_id = upload(client).json["data"]["id"]
    return new_job(client, image_id).json["data"]["id"]


def test_cp07_idempotencia(client):
    register(client)
    image_id = upload(client).json["data"]["id"]
    r1 = new_job(client, image_id)
    r2 = new_job(client, image_id)
    assert r1.status_code == 201 and r2.status_code == 200
    assert r1.json["data"]["id"] == r2.json["data"]["id"]
    assert db.session.query(ProcessingJob).count() == 1


def test_cp08_dos_workers(client):
    _job(client)
    c1, c2 = db.engine.connect(), db.engine.connect()
    t1, t2 = c1.begin(), c2.begin()
    r1 = c1.execute(CLAIM_SQL).first()
    r2 = c2.execute(CLAIM_SQL).first()                                         # SKIP LOCKED: no lo ve
    t1.commit(); t2.commit(); c1.close(); c2.close()
    assert r1 is not None and r2 is None


def test_cp09_fallo_del_motor(client, app):
    job_id = _job(client)
    for _ in range(app.config["AI_MAX_ATTEMPTS"]):
        process_one(app, None)                                                 # motor sin pesos
    job = db.session.get(ProcessingJob, job_id)
    assert job.status == "failed" and job.error_code == "modelo_no_disponible"
    assert db.session.query(ServiceIncident).count() == 1
    assert "Traceback" not in client.get(f"/api/v1/jobs/{job_id}").get_data(as_text=True)


class _NoFileEngine(HumanizationEngine):
    def humanize(self, input_path, output_path, preset, seed=None):
        return {"model_id": "x", "model_version": "x"}                         # «olvida» guardar el archivo


def test_rnf07_completed_solo_con_archivo(client, app):
    job_id = _job(client)
    for _ in range(app.config["AI_MAX_ATTEMPTS"]):
        process_one(app, _NoFileEngine())
    job = db.session.get(ProcessingJob, job_id)
    assert job.status == "failed" and job.error_code == "resultado_inexistente"


def test_cp11_acceso_cruzado(client, other_client, app):
    job_id = _job(client)
    process_one(app, MockEngine())
    register(other_client, "b@demo.pe")
    image_id = db.session.get(ProcessingJob, job_id).image_id
    assert other_client.get(f"/api/v1/jobs/{job_id}").status_code == 404
    assert other_client.get(f"/api/v1/jobs/{job_id}/download").status_code == 404
    assert other_client.get(f"/api/v1/images/{image_id}/content").status_code == 404


def test_cp12_descarga_autorizada(client, app):
    job_id = _job(client)
    process_one(app, MockEngine())
    r = client.get(f"/api/v1/jobs/{job_id}/download")
    assert r.status_code == 200
    assert "editado_IA" in r.headers["Content-Disposition"]                    # RF-16: en el nombre
    assert b"editado con IA" in r.data                                         # RF-16: en los metadatos
    assert db.session.query(AuditEvent).filter_by(action="job.download", entity_id=job_id).count() == 1


def test_rnf10_trazabilidad(client, app):
    job_id = _job(client)
    process_one(app, MockEngine())
    data = client.get(f"/api/v1/jobs/{job_id}").json["data"]
    assert data["status"] == "completed" and data["model_id"] == "mock"
    assert {"strength", "steps", "guidance", "seed"} <= set(data["parameters"])
```

### 11.5 `backend/tests/test_equipos.py` (F4: RF-18 a RF-21)

```python
from datetime import timedelta
from app.extensions import db, utc_now
from app.models import TeamInvitation, User
from tests.conftest import register, upload


def _team_with_member(app, client, other_client):
    register(client, "owner@demo.pe")
    team_id = client.post("/api/v1/teams", json={"name": "Diseño"}).json["data"]["id"]
    link = client.post(f"/api/v1/teams/{team_id}/invitations").json["data"]["link"]
    token = link.split("token=")[1]
    register(other_client, "member@demo.pe")
    assert other_client.post("/api/v1/invitations/accept", json={"token": token}).status_code == 200
    return team_id, token


def test_rf18_invitacion_un_solo_uso(app, client, other_client):
    _, token = _team_with_member(app, client, other_client)
    third = app.test_client()
    register(third, "c@demo.pe")
    assert third.post("/api/v1/invitations/accept", json={"token": token}).status_code == 400


def test_rf18_invitacion_vencida(app, client, other_client):
    team_id, _ = _team_with_member(app, client, other_client)
    link = client.post(f"/api/v1/teams/{team_id}/invitations").json["data"]["link"]
    inv = db.session.query(TeamInvitation).order_by(TeamInvitation.id.desc()).first()
    inv.expires_at = utc_now() - timedelta(hours=1)
    db.session.commit()
    third = app.test_client()
    register(third, "c@demo.pe")
    assert third.post("/api/v1/invitations/accept", json={"token": link.split("token=")[1]}).status_code == 400


def test_rf19_compartir_explicito(app, client, other_client):
    _team_with_member(app, client, other_client)
    image_id = upload(client).json["data"]["id"]
    assert other_client.get(f"/api/v1/images/{image_id}").status_code == 404   # privada por defecto
    client.patch(f"/api/v1/images/{image_id}/visibility", json={"visibility": "team"})
    assert other_client.get(f"/api/v1/images/{image_id}").status_code == 200


def test_rf20_estadisticas_agregadas(app, client, other_client):
    team_id, _ = _team_with_member(app, client, other_client)
    r = other_client.get(f"/api/v1/teams/{team_id}/stats?days=30")
    assert r.status_code == 200 and "storage_key" not in r.get_data(as_text=True)
    outsider = app.test_client()
    register(outsider, "x@demo.pe")
    assert outsider.get(f"/api/v1/teams/{team_id}/stats").status_code == 404   # CU06 flujo 2a


def test_rf21_admin(app, client):
    register(client)
    assert client.get("/api/v1/admin/overview").status_code == 403            # CU07 flujo 1a
    db.session.query(User).filter_by(email="a@demo.pe").update({"global_role": "admin"})
    db.session.commit()
    r = client.get("/api/v1/admin/overview")
    assert r.status_code == 200 and "original_storage_key" not in r.get_data(as_text=True)
```

### 11.6 Ejecutar pytest

```powershell
cd C:\proyectos\lumia-ai\backend; .\.venv\Scripts\Activate.ps1
pytest -v | Tee-Object -FilePath ..\docs\evidencias\pytest_resultado.txt
```

(Crea antes la carpeta: `mkdir ..\docs\evidencias`.)

📌 **Evidencia:** `docs/evidencias/pytest_resultado.txt`. Cada prueba lleva el código CP o RF en su nombre: con ella llenas las columnas **Obtenido / Evidencia / Estado** de la matriz de pruebas (paso 16).

### 11.7 Vitest (frontend)

**`src/tests/setup.ts`**

```ts
import "@testing-library/jest-dom/vitest";
```

**`src/tests/BeforeAfterSlider.test.tsx`**

```tsx
import { fireEvent, render, screen } from "@testing-library/react";
import { BeforeAfterSlider } from "@/components/BeforeAfterSlider";

test("el comparador se controla con el deslizador accesible", () => {
  render(<BeforeAfterSlider before="/a.png" after="/b.png" />);
  const slider = screen.getByRole("slider", { name: "Comparar antes y después" });
  fireEvent.change(slider, { target: { value: "30" } });
  expect(screen.getByAltText("Imagen original")).toHaveStyle({ clipPath: "inset(0 70% 0 0)" });
  expect(screen.getByAltText("Resultado editado con IA")).toBeInTheDocument();
});
```

**`src/tests/api.test.ts`**

```ts
import { api, ApiError } from "@/lib/api";

test("api convierte el error del servidor en un mensaje legible", async () => {
  globalThis.fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify({ data: null, error: { code: "credenciales", message: "Correo o contraseña incorrectos." } }), { status: 401 }));
  await expect(api("/auth/me")).rejects.toThrow(ApiError);
  await expect(api("/auth/me")).rejects.toThrow("Correo o contraseña incorrectos.");
});
```

En **`frontend/tsconfig.app.json`** agrega `"types": ["vitest/globals"]` dentro de `compilerOptions`. En **`package.json`**, dentro de `"scripts"`, agrega `"test": "vitest run"` y `"e2e": "playwright test"`.

```powershell
cd C:\proyectos\lumia-ai\frontend
npm test | Tee-Object -FilePath ..\docs\evidencias\vitest_resultado.txt
```

### 11.8 Playwright (flujo completo en el navegador)

```powershell
npx playwright install chromium
mkdir e2e\fixtures
```

Copia una imagen sintética autorizada como `frontend/e2e/fixtures/retrato_prueba.png`.

**`frontend/playwright.config.ts`**

```ts
import { defineConfig } from "@playwright/test";
export default defineConfig({ testDir: "./e2e", timeout: 300_000, use: { baseURL: "http://localhost:5000", screenshot: "on" } });
```

**`frontend/e2e/flujo.spec.ts`**

```ts
import { expect, test } from "@playwright/test";

test("registro → carga → humanización → comparación → descarga", async ({ page }) => {
  const email = `e2e+${Date.now()}@demo.pe`;
  await page.goto("/registro");
  await page.getByLabel("Nombre").fill("Prueba E2E");
  await page.getByLabel("Correo").fill(email);
  await page.getByLabel(/Contraseña/).fill("clave-segura-123");
  await page.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page).toHaveURL(/\/app$/);

  await page.goto("/app/humanizar");
  await page.getByLabel("Seleccionar imagen").setInputFiles("e2e/fixtures/retrato_prueba.png");
  await page.getByLabel(/Confirmo que la imagen es generada por IA/).check();
  await page.getByRole("button", { name: "Subir imagen" }).click();
  await page.getByRole("button", { name: "Humanizar imagen" }).click();
  await expect(page.getByRole("link", { name: "Descargar resultado" })).toBeVisible({ timeout: 240_000 });
  await expect(page.getByRole("slider", { name: "Comparar antes y después" })).toBeVisible();
});
```

Con el sistema en marcha en modo demostración (`scripts\iniciar.ps1`):

```powershell
npm run e2e
```

Las capturas quedan en `frontend/test-results/` y también sirven como evidencia.

### 11.9 Medición de rendimiento (RNF-03)

**`backend/tools/medir_api.py`**

```python
"""RNF-03: 20 solicitudes por operación sin IA; reporta la media y el máximo en ms."""
import io
import pathlib
import statistics
import sys
import time
import uuid
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from PIL import Image
from app import create_app

app = create_app(WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False)
c = app.test_client()
c.post("/api/v1/auth/register", json={"email": f"rendimiento+{uuid.uuid4().hex[:6]}@lumia.local",
                                       "display_name": "Medición", "password": "clave-segura-123"})
buf = io.BytesIO(); Image.new("RGB", (512, 512), (180, 140, 120)).save(buf, "PNG"); buf.seek(0)
img_id = c.post("/api/v1/images", data={"file": (buf, "m.png"), "declaracion_ia": "true"},
                content_type="multipart/form-data").json["data"]["id"]

for name, call in [("GET /auth/me", lambda: c.get("/api/v1/auth/me")),
                   ("GET /jobs", lambda: c.get("/api/v1/jobs")),
                   ("GET /images/{id}", lambda: c.get(f"/api/v1/images/{img_id}")),
                   ("GET /workspaces", lambda: c.get("/api/v1/workspaces"))]:
    times = []
    for _ in range(20):
        t0 = time.perf_counter(); call(); times.append((time.perf_counter() - t0) * 1000)
    print(f"{name:20s} media {statistics.mean(times):6.1f} ms   máx {max(times):6.1f} ms")
```

```powershell
cd C:\proyectos\lumia-ai\backend
python tools\medir_api.py | Tee-Object -FilePath ..\docs\evidencias\rnf03_rendimiento.txt
```

---

## 12. Scripts PowerShell (A11)

Guárdalos en `scripts/`, con codificación **UTF-8 con BOM** (en VS Code: abajo a la derecha → «Save with Encoding» → «UTF-8 with BOM») para que se vean bien las tildes.

### 12.1 `scripts/diagnostico.ps1`

```powershell
# Verifica requisitos de la PC (skill §11). No instala nada.
$ErrorActionPreference = "Continue"
Write-Host "== Diagnóstico LUMIA AI ==" -ForegroundColor Cyan
"Windows : " + (Get-CimInstance Win32_OperatingSystem).Caption + " " + (Get-CimInstance Win32_OperatingSystem).OSArchitecture
"Equipo  : " + (Get-CimInstance Win32_ComputerSystem).Manufacturer + " " + (Get-CimInstance Win32_ComputerSystem).Model
"CPU     : " + (Get-CimInstance Win32_Processor | Select-Object -First 1).Name
"RAM     : {0} GB" -f [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
"Disco C : {0} GB libres" -f [math]::Round((Get-PSDrive C).Free / 1GB, 1)
$faltan = 0
foreach ($cmd in "python", "node", "npm", "psql", "nvidia-smi") {
    $c = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($c) { Write-Host ("{0,-11} OK   {1}" -f $cmd, $c.Source) -ForegroundColor Green }
    else { Write-Host ("{0,-11} FALTA" -f $cmd) -ForegroundColor Red; $faltan++ }
}
if (Get-Command python -ErrorAction SilentlyContinue) {
    $v = python --version
    if ($v -notmatch "3\.12") { Write-Warning "Se recomienda Python 3.12 (encontrado: $v)" }
}
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
} else { Write-Warning "Sin GPU NVIDIA: el motor local funcionará en CPU (muy lento) o solo con AI_ENGINE=mock." }
$svc = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
if ($svc) { "PostgreSQL servicio: " + ($svc | Select-Object -First 1).Status } else { Write-Warning "No se encontró el servicio de PostgreSQL." }
if ($faltan -gt 0) { Write-Host "Faltan $faltan programas. Instálalos antes de continuar." -ForegroundColor Red; exit 1 }
Write-Host "Diagnóstico correcto." -ForegroundColor Green
```

### 12.2 `scripts/instalar.ps1`

```powershell
# Instala dependencias del proyecto, compila el frontend y aplica migraciones.
# No instala PostgreSQL ni controladores (skill §11).
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Warning "Se creó .env. Completa SECRET_KEY, DATABASE_URL, AI_MODEL_ID y AI_MODEL_PATH y vuelve a ejecutar."
    exit 1
}
if (-not (Select-String -Path ".env" -Pattern "^SECRET_KEY=.+")) { Write-Error "SECRET_KEY está vacío en .env" }
New-Item -ItemType Directory -Force "private_data\originals", "private_data\results", "docs\evidencias" | Out-Null

Write-Host "1/4 Entorno de Python" -ForegroundColor Cyan
Set-Location "$root\backend"
if (-not (Test-Path ".venv")) { python -m venv .venv }
$py = "$root\backend\.venv\Scripts\python.exe"
& $py -m pip install --upgrade pip
& $py -m pip install -e ".[dev]"

Write-Host "2/4 PyTorch y motor de IA" -ForegroundColor Cyan
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    & $py -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
} else {
    Write-Warning "Sin GPU NVIDIA: se instala PyTorch para CPU."
    & $py -m pip install torch torchvision
}
& $py -m pip install -e ".[ia]"

Write-Host "3/4 Migraciones de PostgreSQL" -ForegroundColor Cyan
& "$root\backend\.venv\Scripts\alembic.exe" upgrade head

Write-Host "4/4 Frontend" -ForegroundColor Cyan
Set-Location "$root\frontend"
npm ci
npm run build

$model = (Select-String -Path "$root\.env" -Pattern "^AI_MODEL_PATH=(.+)$").Matches.Groups[1].Value
if (-not $model -or -not (Test-Path (Join-Path $root $model))) {
    Write-Warning "No se encuentran los pesos del modelo en '$model'. Cópialos antes de usar AI_ENGINE=local."
}
Write-Host "Instalación completa. Ejecuta scripts\iniciar.ps1" -ForegroundColor Green
```

### 12.3 `scripts/iniciar.ps1`

```powershell
# Levanta la API (waitress) y el worker, y abre el navegador (modo demostración).
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$py = "$root\backend\.venv\Scripts\python.exe"
if (-not (Test-Path "$root\.env")) { Write-Error "Falta .env: copia .env.example y complétalo." }
if (-not (Test-Path $py)) { Write-Error "Falta el entorno de Python: ejecuta scripts\instalar.ps1" }

$envs = @{}
Get-Content "$root\.env" | Where-Object { $_ -match "^\s*([A-Z_]+)=(.*)$" } | ForEach-Object { $envs[$Matches[1]] = $Matches[2].Trim() }
foreach ($k in "SECRET_KEY", "DATABASE_URL") { if (-not $envs[$k]) { Write-Error "Falta $k en .env" } }
if ($envs["AI_ENGINE"] -eq "local" -and -not (Test-Path (Join-Path $root $envs["AI_MODEL_PATH"]))) {
    Write-Error "AI_ENGINE=local pero no están los pesos en $($envs['AI_MODEL_PATH'])"
}
if ($envs["AI_ENGINE"] -ne "local") { Write-Warning "AI_ENGINE=$($envs['AI_ENGINE']): SIMULACIÓN, SIN IA REAL" }
if (-not (Test-Path "$root\frontend\dist\index.html")) { Write-Error "Falta compilar el frontend: ejecuta scripts\instalar.ps1" }
if (Test-Path "$PSScriptRoot\.pids") { Write-Error "LUMIA AI ya parece estar en marcha. Ejecuta scripts\detener.ps1 primero." }

& $py -c "import sys; sys.path.insert(0, r'$root\backend'); from app import create_app; from app.extensions import db; a=create_app(); a.app_context().push(); db.session.execute(db.text('SELECT 1')); print('Base de datos: OK')"
if ($LASTEXITCODE -ne 0) { Write-Error "No se pudo conectar con PostgreSQL. Revisa el servicio y DATABASE_URL." }

$pids = @()
$api = Start-Process $py -ArgumentList "-m", "waitress", "--listen=127.0.0.1:5000", "wsgi:app" `
       -WorkingDirectory "$root\backend" -PassThru -WindowStyle Minimized
$pids += $api.Id
$n = [int]($envs["AI_WORKER_CONCURRENCY"]); if ($n -lt 1) { $n = 1 }
for ($i = 1; $i -le $n; $i++) {
    $w = Start-Process $py -ArgumentList "-m", "app.workers.image_worker" -WorkingDirectory "$root\backend" -PassThru -WindowStyle Minimized
    $pids += $w.Id
}
$pids | Set-Content "$PSScriptRoot\.pids"

$ok = $false
for ($i = 0; $i -lt 30; $i++) {
    try { Invoke-RestMethod http://127.0.0.1:5000/api/v1/health -TimeoutSec 2 | Out-Null; $ok = $true; break } catch { Start-Sleep 1 }
}
if (-not $ok) { Write-Error "La API no respondió en 30 s. Revisa la ventana minimizada de la API." }
Start-Process "http://localhost:5000"
Write-Host "LUMIA AI en marcha (procesos: $($pids -join ', ')). Para cerrar: scripts\detener.ps1" -ForegroundColor Green
```

### 12.4 `scripts/detener.ps1`

```powershell
# Cierra SOLO los procesos que abrió iniciar.ps1 (no toca PostgreSQL ni otros servicios).
$file = "$PSScriptRoot\.pids"
if (-not (Test-Path $file)) { Write-Host "No hay procesos de LUMIA AI registrados."; exit 0 }
Get-Content $file | ForEach-Object {
    $p = Get-Process -Id $_ -ErrorAction SilentlyContinue
    if ($p -and $p.ProcessName -like "python*") { Stop-Process -Id $_ -Force; "Detenido proceso $_" }
}
Remove-Item $file
Write-Host "LUMIA AI detenido." -ForegroundColor Green
```

### 12.5 `backend/tools/verificar_circuito.py` (lo usa `verificar.ps1`)

```python
"""Ejecuta un trabajo de inferencia REAL de punta a punta con una imagen autorizada (skill §11)."""
import pathlib
import sys
import time
import uuid
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from app import create_app

muestra = pathlib.Path(sys.argv[1])
app = create_app(WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False)
if app.config["AI_ENGINE"] != "local":
    sys.exit("AI_ENGINE no es 'local': esta verificación NO prueba IA real.")
c = app.test_client()
r = c.post("/api/v1/auth/register", json={"email": f"verificacion+{uuid.uuid4().hex[:8]}@lumia.local",
                                           "display_name": "Verificación", "password": "clave-segura-123"})
assert r.status_code == 201, r.json
with muestra.open("rb") as f:
    r = c.post("/api/v1/images", data={"file": (f, muestra.name), "declaracion_ia": "true"}, content_type="multipart/form-data")
assert r.status_code == 201, r.json
r = c.post("/api/v1/jobs", json={"image_id": r.json["data"]["id"], "preset": "natural"}, headers={"Idempotency-Key": uuid.uuid4().hex})
job_id = r.json["data"]["id"]
t0 = time.time()
while time.time() - t0 < 600:
    job = c.get(f"/api/v1/jobs/{job_id}").json["data"]
    if job["status"] in ("completed", "failed"):
        break
    time.sleep(3)
print(f"Trabajo {job_id}: {job['status']} en {round(time.time() - t0, 1)} s · modelo {job['model_id']} {job['model_version']}")
print(f"Parámetros: {job['parameters']}")
assert job["status"] == "completed", f"Falló: {job['error_code']}"
d = c.get(f"/api/v1/jobs/{job_id}/download")
assert d.status_code == 200 and b"editado con IA" in d.data, "El resultado no está rotulado"
print("Inferencia real verificada: OK")
```

### 12.6 `scripts/verificar.ps1`

```powershell
# Health check, BD autenticada, migraciones, pruebas mínimas e inferencia real (skill §11, CP-14).
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$py = "$root\backend\.venv\Scripts\python.exe"
$muestra = "$root\docs\muestra_autorizada.png"
$log = "$root\docs\evidencias\verificar_$(Get-Date -Format yyyyMMdd_HHmm).txt"
Start-Transcript -Path $log | Out-Null
try {
    Write-Host "1/5 Salud de la API" -ForegroundColor Cyan
    $h = (Invoke-RestMethod http://127.0.0.1:5000/api/v1/health).data
    $h | Format-List
    if ($h.engine -ne "local") { throw "AI_ENGINE no es local: la verificación final exige IA real." }

    Write-Host "2/5 Conexión autenticada y migraciones" -ForegroundColor Cyan
    Push-Location "$root\backend"
    & .\.venv\Scripts\alembic.exe current
    & .\.venv\Scripts\alembic.exe check
    if ($LASTEXITCODE -ne 0) { throw "El esquema no coincide con los modelos." }

    Write-Host "3/5 Pruebas automatizadas mínimas" -ForegroundColor Cyan
    & .\.venv\Scripts\pytest.exe -q
    if ($LASTEXITCODE -ne 0) { throw "Hay pruebas fallidas." }
    Pop-Location

    Write-Host "4/5 Worker activo" -ForegroundColor Cyan
    if ($null -eq $h.worker_seconds_since_beat -or $h.worker_seconds_since_beat -gt 30) { throw "El worker no está en marcha." }
    "Worker: OK"

    Write-Host "5/5 Inferencia real con imagen autorizada" -ForegroundColor Cyan
    if (-not (Test-Path $muestra)) { throw "Falta $muestra (imagen sintética autorizada)." }
    & $py "$root\backend\tools\verificar_circuito.py" $muestra
    if ($LASTEXITCODE -ne 0) { throw "La inferencia real falló." }

    Write-Host "VERIFICACIÓN COMPLETA: todo correcto." -ForegroundColor Green
} catch {
    Write-Host "VERIFICACIÓN FALLIDA: $_" -ForegroundColor Red
    exit 1
} finally {
    Stop-Transcript | Out-Null
    Write-Host "Registro guardado en $log"
}
```

> Copia una de tus muestras autorizadas como `docs\muestra_autorizada.png`. No la subas a Git si no tienes permiso para publicarla: en ese caso agrega `docs/muestra_autorizada.png` al `.gitignore`.

---

## 13. Evaluación del motor con el protocolo del Anexo A (A09)

### 13.1 `backend/app/ai/evaluation.py`

```python
"""Evaluación del motor (Anexo A).
  1) python -m app.ai.evaluation procesar  C:\\lumia_muestras  C:\\lumia_eval
  2) python -m app.ai.evaluation preparar  C:\\lumia_eval  --preset natural
  3) (los revisores llenan las fichas)
  4) python -m app.ai.evaluation resumir   C:\\lumia_eval
"""
import argparse
import csv
import random
import shutil
import statistics
from pathlib import Path
from app.ai.prompts import PRESETS

EXT = {".png", ".jpg", ".jpeg", ".webp"}
FICHA = ["muestra", "revisor", "defecto_principal", "regeneraciones_previas", "minutos_retoque",
         "naturalidad_A", "naturalidad_B", "misma_persona", "conserva_pose_ropa_fondo", "artefactos", "observaciones"]


def procesar(muestras: Path, salida: Path):
    from app import create_app
    from app.ai.local_engine import LocalHumanizationEngine
    app = create_app()
    eng = LocalHumanizationEngine(str(app.config["AI_MODEL_PATH"]), app.config["AI_MODEL_ID"])
    lp = None
    try:
        import lpips, torch                                       # opcional (R. Zhang et al., 2018)
        from PIL import Image
        import torchvision.transforms.functional as TF
        lp = lpips.LPIPS(net="alex")
    except Exception:
        print("LPIPS no disponible: se omite.")
    (salida / "resultados").mkdir(parents=True, exist_ok=True)
    rows = []
    for src in sorted(p for p in muestras.iterdir() if p.suffix.lower() in EXT):
        for preset in PRESETS:
            dst = salida / "resultados" / f"{src.stem}_{preset}.png"
            meta = eng.humanize(str(src), str(dst), preset)
            row = {"muestra": src.stem, **{k: meta.get(k) for k in ("preset", "strength", "steps", "guidance", "seed",
                                                                    "seconds", "vram_gb", "model_id", "model_version")}}
            if lp:
                a = TF.to_tensor(Image.open(src).convert("RGB").resize((256, 256))) * 2 - 1
                b = TF.to_tensor(Image.open(dst).convert("RGB").resize((256, 256))) * 2 - 1
                row["lpips"] = round(float(lp(a[None], b[None])), 4)
            rows.append(row)
            print(row)
    with (salida / "resultados.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print(f"Listo: {salida / 'resultados.csv'}")


def preparar(salida: Path, muestras: Path, preset: str, revisores: int):
    """Pares a ciegas: A/B en orden aleatorio; la clave queda aparte para la autora."""
    ciego = salida / "revision_a_ciegas"
    ciego.mkdir(parents=True, exist_ok=True)
    clave = []
    for res in sorted((salida / "resultados").glob(f"*_{preset}.png")):
        stem = res.stem.rsplit(f"_{preset}", 1)[0]
        orig = next(p for p in muestras.iterdir() if p.stem == stem and p.suffix.lower() in EXT)
        a_es_original = random.random() < 0.5
        shutil.copy(orig if a_es_original else res, ciego / f"{stem}_A{(orig if a_es_original else res).suffix}")
        shutil.copy(res if a_es_original else orig, ciego / f"{stem}_B{(res if a_es_original else orig).suffix}")
        clave.append({"muestra": stem, "A": "original" if a_es_original else "resultado"})
    with (salida / "clave_NO_ENTREGAR_A_REVISORES.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["muestra", "A"]); w.writeheader(); w.writerows(clave)
    for r in range(1, revisores + 1):
        with (salida / f"ficha_revisor_{r}.csv").open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=FICHA); w.writeheader()
            for c in clave:
                w.writerow({"muestra": c["muestra"], "revisor": f"R{r}"})
    print(f"Entrega a cada revisor la carpeta {ciego} y su ficha_revisor_N.csv (escala 1 a 5).")


def resumir(salida: Path):
    clave = {r["muestra"]: r["A"] for r in csv.DictReader((salida / "clave_NO_ENTREGAR_A_REVISORES.csv").open(encoding="utf-8-sig"))}
    nat_o, nat_r, ident, conserva, artef = [], [], [], [], []
    for ficha in salida.glob("ficha_revisor_*.csv"):
        for r in csv.DictReader(ficha.open(encoding="utf-8-sig")):
            if not r["naturalidad_A"]:
                continue
            a, b = float(r["naturalidad_A"]), float(r["naturalidad_B"])
            o, res = (a, b) if clave[r["muestra"]] == "original" else (b, a)
            nat_o.append(o); nat_r.append(res); ident.append(float(r["misma_persona"]))
            conserva.append(r["conserva_pose_ropa_fondo"].strip().lower() in ("si", "sí"))
            artef.append(r["artefactos"].strip().lower() == "graves")
    n = len(nat_o)
    print(f"Respuestas: {n}")
    print(f"Naturalidad media original : {statistics.mean(nat_o):.2f} / 5")
    print(f"Naturalidad media resultado: {statistics.mean(nat_r):.2f} / 5")
    print(f"Pares en que el resultado se ve más natural: {sum(r > o for o, r in zip(nat_o, nat_r)) / n:.0%}")
    print(f"Identidad media (misma persona): {statistics.mean(ident):.2f} / 5")
    print(f"Conserva pose, ropa, encuadre y fondo: {sum(conserva) / n:.0%}")
    print(f"Artefactos graves: {sum(artef) / n:.0%}")
    times = [float(r["seconds"]) for r in csv.DictReader((salida / "resultados.csv").open(encoding="utf-8-sig"))]
    print(f"Tiempo de inferencia medio: {statistics.mean(times):.1f} s (mín {min(times):.1f} · máx {max(times):.1f})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("procesar"); p1.add_argument("muestras", type=Path); p1.add_argument("salida", type=Path)
    p2 = sub.add_parser("preparar"); p2.add_argument("salida", type=Path); p2.add_argument("--muestras", type=Path, default=Path(r"C:\lumia_muestras"))
    p2.add_argument("--preset", default="natural"); p2.add_argument("--revisores", type=int, default=3)
    p3 = sub.add_parser("resumir"); p3.add_argument("salida", type=Path)
    a = ap.parse_args()
    if a.cmd == "procesar": procesar(a.muestras, a.salida)
    elif a.cmd == "preparar": preparar(a.salida, a.muestras, a.preset, a.revisores)
    else: resumir(a.salida)
```

### 13.2 Procedimiento

```powershell
cd C:\proyectos\lumia-ai\backend; .\.venv\Scripts\Activate.ps1
# 1) Procesar todas las muestras con los 3 presets (anota tiempo y VRAM automáticamente)
python -m app.ai.evaluation procesar C:\lumia_muestras C:\lumia_eval
# 2) Revisa C:\lumia_eval\resultados\ y elige el mejor preset; ajusta prompts.py si hace falta y repite el paso 1
# 3) Preparar pares a ciegas para 3 revisores
python -m app.ai.evaluation preparar C:\lumia_eval --preset natural --revisores 3
# 4) Cada revisor llena su ficha_revisor_N.csv (Excel) mirando revision_a_ciegas\
# 5) Calcular los resultados
python -m app.ai.evaluation resumir C:\lumia_eval | Tee-Object -FilePath C:\proyectos\lumia-ai\docs\evidencias\evaluacion_motor.txt
```

**Criterios de ajuste:**
- Si la persona cambia (identidad media < 4): baja `strength` 0,04 en `prompts.py`.
- Si casi no hay mejora (naturalidad del resultado ≈ la del original): sube `strength` 0,04, sin pasar de 0,40.
- Si los 3 presets se ven iguales: deja solo `natural` en `PRESETS` (la web mostrará un solo botón, como pide el skill).
- Manos y cuerpo completo: anótalos aparte. Solo se anuncian si mejoran en las pruebas.

📌 **Evidencias:** `resultados.csv`, las 3 fichas llenas, `evaluacion_motor.txt` y 2 o 3 pares antes/después **autorizados** para el informe y para la landing (con `DEMO_REAL = true`).

---

## 14. Instalación en otra PC (CP-14, A11)

1. Copia en una memoria USB: la carpeta `lumia-ai` **sin** `backend\.venv`, `frontend\node_modules`, `private_data` ni `.env`. Copia aparte `models\stable-diffusion-v1-5`.
2. En la PC destino, instala lo del paso 1.1 y crea la base y el usuario (paso 3; la base `lumia_test` también, porque `verificar.ps1` ejecuta pytest).
3. Copia el proyecto a `C:\proyectos\lumia-ai` y los pesos a `C:\proyectos\lumia-ai\models\`.
4. Ejecuta y **cronometra** todo:

```powershell
cd C:\proyectos\lumia-ai
$t = Get-Date
.\scripts\diagnostico.ps1
Copy-Item .env.example .env        # completa SECRET_KEY, DATABASE_URL, AI_ENGINE=local, AI_MODEL_ID, AI_MODEL_PATH
notepad .env
.\scripts\instalar.ps1
.\scripts\iniciar.ps1
.\scripts\verificar.ps1
"Tiempo total: {0:N0} minutos" -f ((Get-Date) - $t).TotalMinutes
.\scripts\detener.ps1
```

5. 📌 **Evidencia CP-14:** el archivo `docs\evidencias\verificar_*.txt` con «VERIFICACIÓN COMPLETA», la salida de `diagnostico.ps1` de esa PC y el tiempo medido. Escríbelos en `docs/instalacion-otra-pc.md`.

**Respaldo y restauración (RNF-08):**

```powershell
mkdir C:\respaldos -Force
pg_dump -U lumia_app -d lumia -F c -f "C:\respaldos\lumia_$(Get-Date -Format yyyyMMdd).dump"
# Restaurar (prueba en lumia_test para no tocar la real):
pg_restore -U lumia_app -d lumia_test -c "C:\respaldos\lumia_AAAAMMDD.dump"
```

**Prueba de caída del worker (RNF-08):** con un trabajo en «Procesando», cierra la ventana del worker. Vuelve a abrirlo después de 15 minutos (o baja `STALE_MINUTES` para la prueba): el trabajo vuelve a la cola y se completa. Toma capturas antes y después.

---

## 15. Documentación del repositorio (docs/)

**`docs/estado.md`** (criterio de aceptación 10: qué está implementado, qué está probado y qué falta):

```markdown
# Estado de LUMIA AI

| # | Criterio de aceptación (skill §14) | Implementado | Probado | Evidencia |
|---|---|---|---|---|
| 1 | La landing pública carga sin sesión y comunica la humanización | ☐ | ☐ | captura |
| 2 | Registro, login, logout y permisos | ☐ | ☐ | pytest test_auth |
| 3 | Carga válida crea original privado y trabajo; inválida se rechaza | ☐ | ☐ | pytest test_imagenes |
| 4 | Modelo real comprobado y evaluado visualmente | ☐ | ☐ | evaluacion_motor.txt |
| 5 | Estado, historial, comparación y descarga con autorización | ☐ | ☐ | pytest test_trabajos, e2e |
| 6 | Otro usuario no accede al original ni al resultado ajeno | ☐ | ☐ | CP-11 |
| 7 | Diseño cuidado en móvil y escritorio, accesible | ☐ | ☐ | capturas 360 px y escritorio |
| 8 | Migraciones y pruebas ejecutadas con resultados documentados | ☐ | ☐ | pytest_resultado.txt |
| 9 | Instalación repetida en otra PC compatible | ☐ | ☐ | verificar_*.txt |
| 10 | Declaración precisa de lo implementado, probado y pendiente | ☐ | ☐ | este archivo |

## Diferencias con el informe
- (anota aquí cualquier cambio de nombre, tabla, endpoint o parámetro)

## Pendientes
- ...
```

**`docs/motor-ia.md`**: el hardware (paso 1.3), el modelo y el repositorio exacto, la licencia del código y de los pesos con su fecha de consulta, las versiones de torch, diffusers y transformers, los parámetros finales de cada preset y los resultados del paso 13 (tiempo, VRAM, naturalidad, identidad y limitaciones encontradas).

**`docs/instalacion-otra-pc.md`**: el paso 14 con los requisitos **medidos**, el tiempo real de instalación y los errores encontrados con su solución.

**`docs/desarrollo-local.md`**: el paso 10.12 (las tres ventanas y el modo demostración).

**`docs/arquitectura.md`**, **`docs/modelo-datos.md`** y **`docs/permisos.md`**: copia el diagrama de arquitectura del skill §3, la lista de las 8 tablas con sus restricciones (sácala de `\d` en psql, de la migración real) y la tabla de actores y permisos del informe (4.1.3).

**`README.md`**: qué es LUMIA AI (2 líneas), los requisitos, el arranque rápido (`instalar` → `iniciar` → `verificar`) y los enlaces a `docs/`.

---

## 16. Lista de evidencias y qué cambiar en el informe (A12)

### 16.1 Evidencias que debes juntar

| Evidencia | Archivo | Para el informe |
|---|---|---|
| Hardware de tu laptop y precio real | paso 1.3 | Costos, depreciación (`datos.py`) |
| Versiones de torch, diffusers y transformers | `pip show` | Referencia APA de Diffusers, 4.5 |
| Licencia de los pesos y su fecha | `docs/motor-ia.md` | 4.4 o 4.5 (motor) |
| `\dt` y `\d processing_jobs` | capturas | 4.3.8–4.3.11 (el modelo de datos coincide) |
| `pytest_resultado.txt` | `docs/evidencias/` | Matriz de pruebas: Obtenido / Evidencia / Estado |
| `vitest_resultado.txt` y capturas de Playwright | `docs/evidencias/`, `test-results/` | Matriz de pruebas, RNF-06 |
| `rnf03_rendimiento.txt` | `docs/evidencias/` | RNF-03 |
| `evaluacion_motor.txt`, `resultados.csv` y fichas | `C:\lumia_eval`, `docs/evidencias/` | Cap. VI (indicadores), Anexo A, CP-10 |
| `verificar_*.txt` de la otra PC y tiempo medido | `docs/evidencias/` | CP-14, RNF-09, 4.5.12 |
| Respaldo restaurado y caída del worker | capturas | RNF-08 |
| Capturas: landing, login, panel, estudio con imagen, «Procesando», comparador, historial, detalle, equipo, admin, vista móvil | `docs/evidencias/capturas/` | 4.5.13 |

### 16.2 Relación entre los casos de prueba del informe y las pruebas

| CP | Prueba automática o manual |
|---|---|
| CP-01 | `test_cp01_registro_valido` |
| CP-02 | `test_cp02_correo_existente` |
| CP-03 | `test_cp03_login_invalido` |
| CP-04 | `test_cp04_carga_jpg_valida` (además, carga manual de un retrato JPG de unos 2 MB) |
| CP-05 | `test_cp05_extension_falsa` |
| CP-06 | `test_cp06_sin_declaracion` + botón deshabilitado en la web (captura) |
| CP-07 | `test_cp07_idempotencia` |
| CP-08 | `test_cp08_dos_workers` |
| CP-09 | `test_cp09_fallo_del_motor` (además, manual: renombra la carpeta del modelo, procesa una imagen y verifica `failed`) |
| CP-10 | Paso 13 + `verificar_circuito.py` |
| CP-11 | `test_cp11_acceso_cruzado` |
| CP-12 | `test_cp12_descarga_autorizada` |
| CP-13 | `test_cp13_csrf` |
| CP-14 | `verificar.ps1` en la otra PC |

### 16.3 Cambios que habrá que hacer en el informe

1. **Tabla E1 (endpoints):** agregar `GET /auth/csrf`, `GET /health`, `PATCH /images/{id}/visibility`, `GET /teams/{id}/stats` y `PATCH /admin/incidents/{id}`.
2. **Matriz de pruebas (4.5.11):** llenar Obtenido / Evidencia / Estado con lo real. Si algo falló, se escribe que falló y por qué.
3. **Trazabilidad (Anexo C):** RF-18 a RF-21 ya tienen pruebas (`test_equipos.py`). Si la Fase 4 quedó terminada y probada, cambiar «Por definir en la segunda fase» y, si corresponde, la columna Fase.
4. **Datos de la laptop** (modelo y precio real) en `datos.py`, y volver a generar el Excel y el informe.
5. **Versión exacta de Diffusers** en las referencias.
6. **Cap. VI:** indicadores con los resultados de la evaluación (naturalidad, identidad, tiempo y VRAM).
7. **4.5.13:** las capturas reales.
8. **Cronograma:** si alguna actividad real no terminó en su fecha, cambiar «Ejecutado».
9. Todo lo que anotaste en «Diferencias con el informe» de `docs/estado.md`.

### 16.4 Qué traerme cuando vuelvas

- La carpeta `docs/evidencias/` completa y `docs/estado.md`.
- El modelo y el precio de tu laptop, y las versiones de las librerías.
- Si algo falló: el **texto completo del error** (cópialo, no lo resumas) y en qué paso ocurrió.

Con eso actualizo el informe para que el sistema, el skill y el documento coincidan.

---

## 17. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `RuntimeError: Faltan SECRET_KEY o DATABASE_URL` | `.env` incompleto o en otra carpeta | El `.env` va en `C:\proyectos\lumia-ai\.env` (la raíz, no `backend/`) |
| `psycopg.OperationalError: password authentication failed` | Contraseña o usuario incorrectos | Revisa `DATABASE_URL`; prueba con `psql -U lumia_app -d lumia` |
| `connection refused` en el puerto 5432 | PostgreSQL detenido | `services.msc` → «postgresql-x64-17» → Iniciar |
| Alembic: `interpolation syntax` | La contraseña tiene `%` | Cambia la contraseña del usuario de la base |
| `permission denied for schema public` | La base no pertenece a `lumia_app` | `ALTER DATABASE lumia OWNER TO lumia_app;` (como `postgres`) |
| 403 `csrf` en todas las escrituras | El frontend no envía `X-CSRFToken` | Revisa `lib/api.ts`; usa el proxy de Vite o el modo demostración (mismo origen) |
| 401 en todas las rutas privadas | La cookie de sesión no llega | Entra por `localhost:5173` (proxy) o `localhost:5000`, no mezcles `127.0.0.1` con `localhost` |
| 429 al iniciar sesión | Límite de 5 intentos por minuto | Espera un minuto (es intencional, RNF-01) |
| Los trabajos se quedan «En cola» | El worker no está en marcha | `python -m app.workers.image_worker` o `iniciar.ps1` |
| `failed` con `modelo_no_disponible` | Pesos ausentes, ruta mala o faltan los archivos fp16 | Revisa `AI_MODEL_PATH` y que existan `unet\diffusion_pytorch_model.fp16.safetensors`, etc. |
| `torch.cuda.is_available()` = False | PyTorch sin CUDA o controlador antiguo | Reinstala torch con el `--index-url` de pytorch.org y actualiza el controlador |
| `failed` con `gpu_memoria` | Resolución de trabajo alta | Baja `WORK_SIDE` a 512 en `prompts.py` y cierra otras apps que usen la GPU |
| `contenido_bloqueado` en un retrato normal | Falso positivo del filtro de seguridad | Anótalo en la evaluación; prueba otra semilla o una fuerza menor |
| shadcn: `No Tailwind CSS configuration found` | Falta `@import "tailwindcss"` o el alias `@` | Revisa el paso 10.2 y la primera línea de `globals.css` |
| `npm run build` falla por tipos | Error de TypeScript | Lee el archivo y la línea que indica; corrige y vuelve a compilar |
| Los scripts `.ps1` no se ejecutan | Política de ejecución | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Tildes rotas en la salida de los `.ps1` | Codificación del archivo | Guárdalos como «UTF-8 with BOM» |
