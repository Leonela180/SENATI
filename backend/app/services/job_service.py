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
