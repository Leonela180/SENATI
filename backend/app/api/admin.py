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
