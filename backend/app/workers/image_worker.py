"""Worker de LUMIA AI: toma trabajos de la cola en PostgreSQL sin duplicados (RF-10)."""
import logging
import signal
import sys
import time
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
        src = path_for("originals", job.image.original_storage_key)
        if job.tool == "humanizar":
            if engine is None:
                raise EngineError("modelo_no_disponible")
            meta = engine.humanize(str(src), str(dst), job.preset, seed=(job.parameters or {}).get("seed"))
        else:                                                                # Estudio de edición (CPU)
            meta = EDITOR.apply(job.tool, str(src), str(dst), job.parameters or {})
        if not dst.is_file() or dst.stat().st_size == 0:                     # RNF-07
            raise EngineError("resultado_inexistente")
        job.result_storage_key = key
        job.model_id, job.model_version = meta.get("model_id"), meta.get("model_version")
        job.parameters = {**(job.parameters or {}),
                          **{k: meta[k] for k in ("seconds", "vram_gb", "work_size", "device", "filtro_seguridad", "width", "height") if k in meta}}
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
