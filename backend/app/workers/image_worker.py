"""Worker de LUMIA AI: toma trabajos de la cola en PostgreSQL sin duplicados (RF-10)."""
import logging
import signal
import sys
import time
import threading
from sqlalchemy import text
from app import create_app
from app.ai.editing import EditingEngine
from app.ai.interface import EngineError, MockEngine
from app.extensions import db, utc_now
from app.models import ProcessingJob, ServiceIncident
from app.storage.local_private import new_key, path_for

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("worker")
POLL_SECONDS = 2
EDITOR = EditingEngine()                     # herramientas del Estudio: siempre disponibles, sin GPU
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
        if app.config.get("AI_LOCAL_RUNTIME") == "cpp":
            from app.ai.lite_engine import LiteHumanizationEngine
            from app.config import ROOT
            return LiteHumanizationEngine(
                app.config["AI_CPP_EXECUTABLE"], app.config["AI_CPP_MODEL_PATH"],
                ROOT / "models/stable-diffusion-v1-5", app.config["PRIVATE_STORAGE_ROOT"] / "lite_jobs",
                side=app.config["AI_LITE_WORK_SIDE"], blend=app.config["AI_RESULT_BLEND"],
                detail_intensity=app.config["AI_DETAIL_INTENSITY"],
            )
        from app.ai.resources import require_memory
        require_memory()
        from app.ai.local_engine import LocalHumanizationEngine
        engine = LocalHumanizationEngine(str(app.config["AI_MODEL_PATH"]), app.config["AI_MODEL_ID"])
        log.info("Motor local cargado: %s (%s) en %s", engine.model_id, engine.model_version, engine.device)
        return engine
    except Exception as error:                                               # noqa: BLE001
        code = error.code if isinstance(error, EngineError) else "modelo_no_disponible"
        log.error("No se pudo cargar el motor local: %s", code)
        db.session.add(ServiceIncident(service_name="worker", error_code=code))
        db.session.commit()
        return None                                                          # los trabajos fallarán con código seguro


def heartbeat(app):
    (app.config["PRIVATE_STORAGE_ROOT"] / "worker.heartbeat").write_text(utc_now().isoformat())


def maintain_heartbeat(app, stop):
    while not stop.wait(5):
        try:
            heartbeat(app)
        except OSError:
            log.warning("No se pudo actualizar el latido del worker")


# Errores causados por la imagen (no por el servicio): fallan al primer intento y no son incidentes.
USER_ERRORS = {"sin_rostro"}
# El motor está ocupado por otro trabajo: no es un fallo del trabajo, así que no consume intentos.
BUSY_ERRORS = {"motor_ocupado"}
BUSY_WAIT_SECONDS = 5


def process_one(app, engine) -> bool:
    row = db.session.execute(CLAIM_SQL).first()
    db.session.commit()
    if not row:
        return False
    job = db.session.get(ProcessingJob, row.id)
    key = new_key("png")
    dst = path_for("results", key)
    try:
        src = path_for("originals", job.image.original_storage_key)
        if job.tool in ("humanizar", "realista"):
            if engine is None:
                raise EngineError("modelo_no_disponible")
            options = {"mode": "realista"} if job.tool == "realista" else {}
            meta = engine.humanize(str(src), str(dst), job.preset, seed=(job.parameters or {}).get("seed"), **options)
        else:                                                                # Estudio de edición (CPU)
            meta = EDITOR.apply(job.tool, str(src), str(dst), job.parameters or {})
        if not dst.is_file() or dst.stat().st_size == 0:                     # RNF-07
            raise EngineError("resultado_inexistente")
        job.result_storage_key = key
        job.model_id, job.model_version = meta.get("model_id"), meta.get("model_version")
        job.parameters = {**(job.parameters or {}),
                          **{k: meta[k] for k in ("seconds", "vram_gb", "work_size", "device", "filtro_seguridad", "width", "height",
                                                "strength", "steps", "guidance", "seed", "runtime", "blend", "ram_free_min_gib",
                                                "facial_detail_applied", "eyes_enhanced", "pores_intensity", "facial_detail_method",
                                                "rostro_detectado", "ojos_protegidos", "cobertura_piel", "conversion_mode") if k in meta}}
        job.status, job.error_code, job.finished_at = "completed", None, utc_now()
        log.info("Trabajo %s completado en %s s", job.id, meta.get("seconds"))
    except Exception as e:                                                   # noqa: BLE001
        code = e.code if isinstance(e, EngineError) else "motor_error"
        log.error("Trabajo %s falló (intento %s): %s", job.id, job.attempt_count, code)
        dst.unlink(missing_ok=True)
        job.error_code = code
        busy = code in BUSY_ERRORS
        if busy:                                                             # espera su turno sin perder un intento
            job.status, job.error_code = "queued", None
            job.attempt_count = max(0, job.attempt_count - 1)
        elif code in USER_ERRORS:                                            # la imagen no sirve: reintentar no ayuda
            job.status, job.finished_at = "failed", utc_now()
        elif job.attempt_count < app.config["AI_MAX_ATTEMPTS"]:
            job.status = "queued"                                            # CU03 flujo 4a: se reencola
        else:
            job.status, job.finished_at = "failed", utc_now()                # CU03 flujo 4b
            db.session.add(ServiceIncident(service_name="worker", error_code=code))
        db.session.commit()
        if busy:
            time.sleep(BUSY_WAIT_SECONDS)
        return True
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
        heartbeat(app)
        stop_heartbeat = threading.Event()
        beat_thread = threading.Thread(target=maintain_heartbeat, args=(app, stop_heartbeat), daemon=True)
        beat_thread.start()
        try:
            engine = build_engine(app)
            log.info("Worker listo (motor: %s)", app.config["AI_ENGINE"])
            while running:
                try:
                    if not process_one(app, engine):
                        time.sleep(POLL_SECONDS)
                except Exception:                                            # noqa: BLE001 (BD caída, etc.)
                    log.error("Error del ciclo del worker; reintento en 5 s")
                    db.session.rollback()
                    time.sleep(5)
        finally:
            stop_heartbeat.set()
            beat_thread.join(timeout=1)
    sys.exit(0)


if __name__ == "__main__":
    main()
