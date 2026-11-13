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
