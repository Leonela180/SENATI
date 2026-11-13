import io
import os
import pytest
from PIL import Image as PILImage
from app import create_app
from app.extensions import db


def url_bd_pruebas():
    # base separada (paso 3); TEST_DATABASE_URL permite usar otra
    return os.environ.get("TEST_DATABASE_URL") or os.environ["DATABASE_URL"].rsplit("/", 1)[0] + "/lumia_test"


@pytest.fixture()
def app(tmp_path):
    app = create_app(TESTING=True, WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False, AI_ENGINE="mock",
                     SQLALCHEMY_DATABASE_URI=url_bd_pruebas(), PRIVATE_STORAGE_ROOT=tmp_path)
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def other_client(app):
    return app.test_client()


def image_bytes(fmt="PNG", size=(64, 64)):
    buf = io.BytesIO()
    PILImage.new("RGB", size, (200, 150, 120)).save(buf, fmt)
    buf.seek(0)
    return buf


def register(client, email="a@demo.pe", name="Demo"):
    return client.post("/api/v1/auth/register", json={"email": email, "display_name": name, "password": "clave-segura-123"})


def upload(client, fmt="PNG", name="a.png", size=(64, 64)):
    r = client.post("/api/v1/images", data={"file": (image_bytes(fmt, size), name), "declaracion_ia": "true"},
                    content_type="multipart/form-data")
    return r


def new_job(client, image_id, key="clave-prueba-0001"):
    return client.post("/api/v1/jobs", json={"image_id": image_id}, headers={"Idempotency-Key": key})
