import logging
import time
import click
from flask import Flask, abort, jsonify, request, send_from_directory
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

    if app.config.get("TRUST_PROXY"):
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)   # detrás del túnel de Cloudflare

    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": [app.config["FRONTEND_ORIGIN"]]}}, supports_credentials=True)

    from .api import auth, users, images, jobs, teams, admin, gallery, generations, hours, assistant
    for module in (auth, users, images, jobs, teams, admin, gallery, generations, hours, assistant):
        app.register_blueprint(module.bp, url_prefix="/api/v1")

    @app.before_request
    def validate_json():
        if request.path.startswith("/api/") and request.is_json:
            data = request.get_json(silent=True)
            if not isinstance(data, dict):
                abort(400, description="Envía un objeto JSON válido.")
            for field in ("email", "display_name", "password", "current_password", "new_password",
                          "name", "prompt", "token", "preset", "tool", "visibility", "status", "note"):
                if field in data and data[field] is not None and not isinstance(data[field], str):
                    abort(400, description="Revisa el formato de los datos enviados.")
            for field in ("password", "current_password", "new_password"):
                if isinstance(data.get(field), str) and len(data[field]) > 1024:
                    abort(400, description="La contraseña supera el tamaño permitido.")

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; font-src 'self'; connect-src 'self'; "
            "object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
        )
        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    # ---------- Errores con formato uniforme y sin trazas internas (RF-12) ----------
    @app.errorhandler(CSRFError)
    def _csrf_error(e):
        return jsonify(data=None, error={"code": "csrf", "message": "Falta o venció el token de seguridad. Recarga la página."}), 403

    @app.errorhandler(HTTPException)
    def _http_error(e):
        return jsonify(data=None, error={"code": e.name.lower().replace(" ", "_"), "message": e.description}), e.code

    @app.errorhandler(Exception)
    def _unexpected(e):
        db.session.rollback()
        log.error("Error no controlado: %s", type(e).__name__)
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
            "presets": (["natural"] if app.config.get("AI_LOCAL_RUNTIME") == "cpp" else list(PRESETS)) if app.config["AI_ENGINE"] == "local" else [],
            "runtime": app.config.get("AI_LOCAL_RUNTIME") if app.config["AI_ENGINE"] == "local" else "mock",
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
