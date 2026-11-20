from flask import Blueprint, g, request
from . import fail, ok
from ..extensions import db, limiter, utc_now
from ..models import TeamMembership, TeamInvitation, User, Workspace
from ..services.team_service import _hash
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
    import re
    data = request.get_json(silent=True) or {}
    email = data.get("email") or ""
    name = data.get("display_name") or ""
    if not isinstance(email, str) or not isinstance(name, str):
        return fail("datos_invalidos", "Revisa el nombre y correo de la persona invitada.", 400)
    email, name = email.strip().lower(), name.strip()
    if len(email) > 254 or len(name) > 120 or (email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)):
        return fail("datos_invalidos", "Revisa el nombre y correo de la persona invitada.", 400)
    try:
        data = create_invitation(g.user, team_id, email or None, name or None)
    except TeamError as e:
        return _team_error(e)
    db.session.commit()
    return ok(data, 201)


@bp.post("/invitations/preview")
@limiter.limit("30/hour")
def preview():
    token = (request.get_json(silent=True) or {}).get("token")
    if not isinstance(token, str) or len(token) > 100:
        return fail("invitacion_invalida", "Invitación no disponible.", 404)
    inv = db.session.query(TeamInvitation).filter_by(token_hash=_hash(token)).first()
    if not inv or inv.used_at or inv.expires_at < utc_now():
        return fail("invitacion_invalida", "Invitación vencida, utilizada o no disponible.", 404)
    team = db.session.get(Workspace, inv.team_workspace_id)
    return ok({"team_name": team.name, "email": inv.recipient_email, "display_name": inv.recipient_name})


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


@bp.get("/teams/<int:team_id>/progress")
@login_required
def shared_progress(team_id):
    """Avance por integrante solo sobre material compartido, exclusivo del líder."""
    from sqlalchemy import func, select
    from ..models import Image, ProcessingJob
    membership = get_team_membership_or_404(team_id)
    if membership.role != "owner":
        return fail("solo_propietario", "Solo el líder puede consultar este resumen.", 403)
    members = db.session.execute(select(User.id, User.display_name).join(
        TeamMembership, TeamMembership.user_id == User.id).where(
        TeamMembership.team_workspace_id == team_id).order_by(User.display_name)).all()
    jobs = db.session.execute(select(ProcessingJob.requested_by, ProcessingJob.status, func.count()).join(
        Image, ProcessingJob.image_id == Image.id).where(Image.workspace_id == team_id,
        Image.visibility == "team").group_by(ProcessingJob.requested_by, ProcessingJob.status)).all()
    images = dict(db.session.execute(select(Image.owner_user_id, func.count()).where(
        Image.workspace_id == team_id, Image.visibility == "team").group_by(Image.owner_user_id)).all())
    grouped = {}
    for user_id, status, count in jobs:
        grouped.setdefault(user_id, {})[status] = count
    return ok([{"user_id": user_id, "display_name": name, "shared_images": images.get(user_id, 0),
                **{status: grouped.get(user_id, {}).get(status, 0) for status in ("completed", "queued", "processing", "failed")}}
               for user_id, name in members])
