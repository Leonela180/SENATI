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
