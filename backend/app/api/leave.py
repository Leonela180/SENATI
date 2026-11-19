"""Permisos internos del equipo. El propietario administra; no verifica un cargo legal."""
from datetime import datetime, timedelta, timezone
from flask import Blueprint, abort, g, request
from sqlalchemy import select
from . import fail, ok
from ..extensions import db, limiter, utc_now
from ..models import LeaveRequest, User, audit
from ..services.permission_service import get_team_membership_or_404, login_required

bp = Blueprint("leave", __name__)


def serialize(row):
    user = db.session.get(User, row.user_id)
    return {"id": row.id, "user_id": row.user_id, "display_name": user.display_name,
            "starts_at": row.starts_at.isoformat(), "ends_at": row.ends_at.isoformat(),
            "reason": row.reason, "status": row.status, "review_note": row.review_note,
            "created_at": row.created_at.isoformat(),
            "reviewed_at": row.reviewed_at.isoformat() if row.reviewed_at else None}


@bp.get("/teams/<int:team_id>/leave")
@login_required
def listing(team_id):
    member = get_team_membership_or_404(team_id)
    query = select(LeaveRequest).where(LeaveRequest.team_id == team_id)
    if member.role != "owner":
        query = query.where(LeaveRequest.user_id == g.user.id)
    rows = db.session.scalars(query.order_by(LeaveRequest.created_at.desc()).limit(100)).all()
    return ok([serialize(row) for row in rows])


@bp.post("/teams/<int:team_id>/leave")
@login_required
@limiter.limit("10/hour")
def create(team_id):
    member = get_team_membership_or_404(team_id)
    if member.role == "owner":
        return fail("solo_integrantes", "El líder revisa los permisos de sus integrantes.", 403)
    data = request.get_json(silent=True) or {}
    reason = data.get("reason")
    try:
        start = datetime.fromisoformat(data.get("starts_at", ""))
        end = datetime.fromisoformat(data.get("ends_at", ""))
        if not start.tzinfo or not end.tzinfo:
            raise ValueError()
        start, end = start.astimezone(timezone.utc), end.astimezone(timezone.utc)
    except (ValueError, TypeError):
        return fail("datos_invalidos", "Indica fechas y horas válidas con zona horaria.", 400)
    if not isinstance(reason, str) or not 5 <= len(reason.strip()) <= 500 or not timedelta(0) < end - start <= timedelta(days=31):
        return fail("datos_invalidos", "Revisa el motivo (5 a 500 caracteres) y un intervalo de hasta 31 días.", 400)
    # Serializa solicitudes del mismo usuario para impedir duplicados simultáneos.
    db.session.execute(select(User).where(User.id == g.user.id).with_for_update()).scalar_one()
    overlap = db.session.scalar(select(LeaveRequest.id).where(
        LeaveRequest.team_id == team_id, LeaveRequest.user_id == g.user.id,
        LeaveRequest.status.in_(["pending", "approved"]), LeaveRequest.starts_at < end,
        LeaveRequest.ends_at > start).limit(1))
    if overlap:
        return fail("permiso_superpuesto", "Ya tienes una solicitud pendiente o aprobada en ese intervalo.", 409)
    row = LeaveRequest(team_id=team_id, user_id=g.user.id, starts_at=start, ends_at=end, reason=reason.strip(), status="pending")
    db.session.add(row)
    db.session.flush()
    audit(g.user.id, "leave.create", "leave_request", row.id)
    db.session.commit()
    return ok(serialize(row), 201)


@bp.patch("/teams/<int:team_id>/leave/<int:request_id>")
@login_required
def review(team_id, request_id):
    member = get_team_membership_or_404(team_id)
    row = db.session.scalar(select(LeaveRequest).where(LeaveRequest.id == request_id, LeaveRequest.team_id == team_id).with_for_update())
    if not row or (member.role != "owner" and row.user_id != g.user.id):
        abort(404)
    data = request.get_json(silent=True) or {}
    decision = data.get("status")
    note = data.get("review_note", "")
    if row.status != "pending":
        return fail("ya_resuelto", "Esta solicitud ya fue resuelta.", 409)
    if decision == "cancelled":
        if row.user_id != g.user.id:
            return fail("sin_permiso", "Solo quien solicitó el permiso puede cancelarlo.", 403)
    elif decision in ("approved", "rejected"):
        if member.role != "owner" or row.user_id == g.user.id:
            return fail("sin_permiso", "Solo el líder puede revisar permisos de otros integrantes.", 403)
    else:
        return fail("datos_invalidos", "Elige aprobar, rechazar o cancelar.", 400)
    if not isinstance(note, str) or len(note) > 300:
        return fail("datos_invalidos", "La respuesta admite hasta 300 caracteres.", 400)
    row.status, row.reviewer_id, row.reviewed_at = decision, g.user.id, utc_now()
    row.review_note = note.strip() or None
    audit(g.user.id, "leave.review", "leave_request", row.id, status=decision)
    db.session.commit()
    return ok(serialize(row))
