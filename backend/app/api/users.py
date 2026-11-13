from argon2.exceptions import VerificationError, VerifyMismatchError
from flask import Blueprint, g, request
from . import fail, ok
from .auth import MIN_PASSWORD, ph, user_json
from ..extensions import db
from ..models import Workspace, audit
from ..services.permission_service import login_required, membership_of, personal_workspace

bp = Blueprint("users", __name__)


@bp.patch("/users/me")
@login_required
def edit_profile():
    name = ((request.get_json(silent=True) or {}).get("display_name") or "").strip()
    if not (1 <= len(name) <= 120):
        return fail("nombre_invalido", "El nombre debe tener entre 1 y 120 caracteres.", 400)
    g.user.display_name = name
    audit(g.user.id, "user.update_profile", "user", g.user.id)
    db.session.commit()
    return ok(user_json(g.user))


@bp.post("/users/me/change-password")
@login_required
def change_password():
    d = request.get_json(silent=True) or {}
    try:
        ph.verify(g.user.password_hash, d.get("current_password") or "")
    except (VerifyMismatchError, VerificationError):
        return fail("clave_actual", "La contraseña actual no es correcta.", 400)
    new = d.get("new_password") or ""
    if len(new) < MIN_PASSWORD:
        return fail("clave_corta", f"La nueva contraseña debe tener al menos {MIN_PASSWORD} caracteres.", 400)
    g.user.password_hash = ph.hash(new)
    audit(g.user.id, "user.change_password", "user", g.user.id)
    db.session.commit()
    return ok({"changed": True})


@bp.get("/workspaces")
@login_required
def workspaces():
    ws = personal_workspace(g.user)
    items = [{"id": ws.id, "name": ws.name, "kind": "personal", "role": "owner"}]
    m = membership_of(g.user)
    if m:
        team = db.session.get(Workspace, m.team_workspace_id)
        items.append({"id": team.id, "name": team.name, "kind": "team", "role": m.role})
    return ok(items)
