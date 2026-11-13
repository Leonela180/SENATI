from argon2 import PasswordHasher
from app import create_app
from app.extensions import db
from app.models import User, Workspace
from tests.conftest import register, url_bd_pruebas


def test_cp01_registro_valido(client):
    r = register(client)
    assert r.status_code == 201
    user = db.session.query(User).filter_by(email="a@demo.pe").one()
    assert db.session.query(Workspace).filter_by(owner_user_id=user.id, kind="personal").count() == 1
    assert user.password_hash.startswith("$argon2id$")                       # RNF-01: sin contraseñas en claro
    assert client.get("/api/v1/auth/me").status_code == 200                   # sesión abierta


def test_cp02_correo_existente(client, other_client):
    register(client)
    r = register(other_client)
    assert r.status_code == 409
    assert db.session.query(User).count() == 1


def test_cp03_login_invalido(client, other_client):
    register(client)
    r = other_client.post("/api/v1/auth/login", json={"email": "a@demo.pe", "password": "incorrecta-123"})
    assert r.status_code == 401
    assert r.json["error"]["message"] == "Correo o contraseña incorrectos."
    assert other_client.get("/api/v1/auth/me").status_code == 401


def test_rf03_logout(client):
    register(client)
    assert client.post("/api/v1/auth/logout").status_code == 200
    assert client.get("/api/v1/auth/me").status_code == 401


def test_cp13_csrf(tmp_path):
    app = create_app(TESTING=True, RATELIMIT_ENABLED=False, SQLALCHEMY_DATABASE_URI=url_bd_pruebas(), PRIVATE_STORAGE_ROOT=tmp_path)
    r = app.test_client().post("/api/v1/auth/login", json={"email": "x@demo.pe", "password": "x"})
    assert r.status_code == 403
    assert r.json["error"]["code"] == "csrf"


def test_rnf01_limite_de_intentos(tmp_path):
    app = create_app(TESTING=True, WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=True,
                     SQLALCHEMY_DATABASE_URI=url_bd_pruebas(), PRIVATE_STORAGE_ROOT=tmp_path)
    with app.app_context():
        db.create_all()
        c = app.test_client()
        codes = [c.post("/api/v1/auth/login", json={"email": "x@demo.pe", "password": "x"}).status_code for _ in range(6)]
        db.session.remove()          # suelta la conexión antes de borrar las tablas
        db.drop_all()
    assert codes[-1] == 429


def test_rf05_cambio_de_clave(client):
    register(client)
    bad = client.post("/api/v1/users/me/change-password", json={"current_password": "otra", "new_password": "nueva-clave-456"})
    assert bad.status_code == 400
    ok = client.post("/api/v1/users/me/change-password", json={"current_password": "clave-segura-123", "new_password": "nueva-clave-456"})
    assert ok.status_code == 200
