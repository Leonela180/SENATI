import re
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from flask import Blueprint, g, request, session
from flask_wtf.csrf import generate_csrf
from sqlalchemy.exc import IntegrityError
from . import fail, ok
from ..extensions import db, limiter
from ..models import User, Workspace, audit
from ..services.permission_service import login_required

bp = Blueprint("auth", __name__)
ph = PasswordHasher()                      # Argon2id con parámetros recomendados (RNF-01)
DUMMY_HASH = ph.hash("contrasena-de-relleno-para-igualar-tiempos")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD = 12


def user_json(u):
    return {"id": u.id, "email": u.email, "display_name": u.display_name, "role": u.global_role}


def _open_session(user):
    session.clear()
    session.permanent = True
    session["user_id"] = user.id


@bp.get("/auth/csrf")
def csrf_token():
    return ok({"csrf_token": generate_csrf()})


@bp.post("/auth/register")
@limiter.limit("10/hour")
def register():
    d = request.get_json(silent=True) or {}
    email = (d.get("email") or "").strip().lower()
    name = (d.get("display_name") or "").strip()
    password = d.get("password") or ""
    if not EMAIL_RE.match(email) or len(email) > 254 or not (1 <= len(name) <= 120) or len(password) < MIN_PASSWORD:
        return fail("datos_invalidos", f"Revisa el correo, el nombre y una contraseña de al menos {MIN_PASSWORD} caracteres.", 400)
    if db.session.query(User).filter_by(email=email).first():
        return fail("no_disponible", "No se pudo crear la cuenta. Si ya tienes una, inicia sesión.", 409)   # CP-02
    user = User(email=email, display_name=name, password_hash=ph.hash(password))
    db.session.add(user)
    try:
        db.session.flush()
        db.session.add(Workspace(name=f"Espacio de {name}"[:120], kind="personal", owner_user_id=user.id))
        audit(user.id, "user.register", "user", user.id)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return fail("no_disponible", "No se pudo crear la cuenta. Si ya tienes una, inicia sesión.", 409)
    _open_session(user)
    return ok(user_json(user), 201)


@bp.post("/auth/login")
@limiter.limit("5/minute")                 # CU01 excepción: bloqueo temporal ante muchos intentos
def login():
    d = request.get_json(silent=True) or {}
    email = (d.get("email") or "").strip().lower()
    password = d.get("password") or ""
    user = db.session.query(User).filter_by(email=email).first()
    try:
        if not user or not user.is_active:
            ph.verify(DUMMY_HASH, password + "x")            # mismo tiempo de respuesta
            raise VerifyMismatchError
        ph.verify(user.password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return fail("credenciales", "Correo o contraseña incorrectos.", 401)   # mensaje genérico (CP-03)
    if ph.check_needs_rehash(user.password_hash):
        user.password_hash = ph.hash(password)
    audit(user.id, "user.login", "user", user.id)
    db.session.commit()
    _open_session(user)
    return ok(user_json(user))


@bp.post("/auth/logout")
@login_required
def logout():
    audit(g.user.id, "user.logout", "user", g.user.id)
    db.session.commit()
    session.clear()
    return ok({"logged_out": True})


@bp.get("/auth/me")
@login_required
def me():
    return ok(user_json(g.user))
