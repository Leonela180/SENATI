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
