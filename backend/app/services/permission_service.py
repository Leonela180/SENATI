from functools import wraps
from flask import abort, g, session
from ..extensions import db
from ..models import Image, ProcessingJob, TeamMembership, User, Workspace


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        uid = session.get("user_id")
        user = db.session.get(User, uid) if uid else None
        if not user or not user.is_active:
            abort(401, description="Inicia sesión para continuar.")
        g.user = user
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if g.user.global_role != "admin":
            abort(403, description="Solo el administrador técnico puede ver esta sección.")   # CU07 flujo 1a
        return fn(*args, **kwargs)
    return wrapper


def personal_workspace(user) -> Workspace:
    return db.session.query(Workspace).filter_by(owner_user_id=user.id, kind="personal").one()


def membership_of(user) -> TeamMembership | None:
    return db.session.query(TeamMembership).filter_by(user_id=user.id).first()


def can_view_image(user, image) -> bool:
    if image.owner_user_id == user.id:
        return True
    if image.visibility == "team":                         # RF-19: solo lo compartido explícitamente
        m = membership_of(user)
        return bool(m and m.team_workspace_id == image.workspace_id)
    return False


def get_image_or_404(image_id):
    image = db.session.get(Image, image_id)
    if not image or not can_view_image(g.user, image):
        abort(404, description="No encontrado.")          # RNF-02: nunca revelar si existe
    return image


def get_job_or_404(job_id):
    job = db.session.get(ProcessingJob, job_id)
    if not job or not (job.requested_by == g.user.id or can_view_image(g.user, job.image)):
        abort(404, description="No encontrado.")
    return job


def get_team_membership_or_404(team_id):
    m = membership_of(g.user)
    if not m or m.team_workspace_id != team_id:
        abort(404, description="No encontrado.")          # CU06 flujo 2a
    return m
