import io
from app.extensions import db
from app.models import Image
from tests.conftest import image_bytes, register, upload


def test_cp04_carga_jpg_valida(client, app):
    register(client)
    r = upload(client, fmt="JPEG", name="retrato.jpg", size=(800, 1000))
    assert r.status_code == 201
    img = db.session.get(Image, r.json["data"]["id"])
    path = app.config["PRIVATE_STORAGE_ROOT"] / "originals" / img.original_storage_key
    assert path.is_file()                                                      # almacén privado
    assert "retrato" not in img.original_storage_key                           # nombre aleatorio


def test_cp05_extension_falsa(client):
    register(client)
    fake = io.BytesIO(b"MZ\x90\x00" + b"\x00" * 400)                          # cabecera de un .exe
    r = client.post("/api/v1/images", data={"file": (fake, "virus.png"), "declaracion_ia": "true"},
                    content_type="multipart/form-data")
    assert r.status_code == 400
    assert r.json["error"]["code"] == "imagen_invalida"


def test_cp06_sin_declaracion(client):
    register(client)
    r = client.post("/api/v1/images", data={"file": (image_bytes(), "a.png")}, content_type="multipart/form-data")
    assert r.status_code == 400
    assert r.json["error"]["code"] == "sin_declaracion"


def test_rf06_demasiados_pixeles(client):
    register(client)
    r = upload(client, size=(5000, 5000))                                      # 25 MP > 24 MP
    assert r.status_code == 400
    assert r.json["error"]["code"] == "demasiados_pixeles"


def test_rf08_sin_ruta_publica(client):
    register(client)
    img = db.session.get(Image, upload(client).json["data"]["id"])
    r = client.get(f"/private_data/originals/{img.original_storage_key}")
    assert r.mimetype != "image/png"                                         # nunca se sirve el archivo
