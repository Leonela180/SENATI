"""Galería (álbumes, mover, borrar) y generación con Gemini (con consentimiento y sin red en las pruebas)."""
import base64
import io
import pytest

from PIL import Image as PILImage

from app.api import generations as gen_api
from app.extensions import db
from app.models import Generation, Image, ProcessingJob
from app.services.gemini_service import GeminiError
from tests.conftest import new_job, register, upload


def test_albumes_mover_filtrar_y_borrar(app, client):
    register(client)
    a = client.post("/api/v1/albums", json={"name": "Campaña"}).json["data"]
    assert client.post("/api/v1/albums", json={"name": "Campaña"}).status_code == 409
    i1 = upload(client).json["data"]["id"]
    i2 = client.post("/api/v1/images", data={"file": (upload_bytes(), "b.png"), "declaracion_ia": "true",
                                             "album_id": str(a["id"])}, content_type="multipart/form-data").json["data"]["id"]
    assert client.patch(f"/api/v1/images/{i1}/album", json={"album_id": a["id"]}).status_code == 200
    listing = client.get(f"/api/v1/images?album={a['id']}").json["data"]
    assert {x["id"] for x in listing["items"]} == {i1, i2}
    assert client.get("/api/v1/albums").json["data"][0]["count"] == 2
    # Borrar el álbum no borra las imágenes
    assert client.delete(f"/api/v1/albums/{a['id']}").status_code == 200
    assert client.get("/api/v1/images?album=none").json["data"]["total"] == 2


def test_borrar_imagen_elimina_trabajos_y_archivos(app, client):
    register(client)
    image_id = upload(client).json["data"]["id"]
    new_job(client, image_id)
    original = app.config["PRIVATE_STORAGE_ROOT"] / "originals" / db.session.get(Image, image_id).original_storage_key
    assert original.exists()
    assert client.delete(f"/api/v1/images/{image_id}").status_code == 200
    assert db.session.get(Image, image_id) is None
    assert db.session.query(ProcessingJob).count() == 0
    assert not original.exists()


def test_galeria_es_privada(client, other_client):
    register(client)
    image_id = upload(client).json["data"]["id"]
    register(other_client, "b@demo.pe")
    assert other_client.get("/api/v1/images").json["data"]["total"] == 0
    assert other_client.delete(f"/api/v1/images/{image_id}").status_code == 404


def upload_bytes():
    buf = io.BytesIO()
    PILImage.new("RGB", (32, 32), (10, 120, 200)).save(buf, "PNG")
    buf.seek(0)
    return buf


def test_gemini_exige_consentimiento(app, client):
    register(client)
    r = client.post("/api/v1/generations", json={"prompt": "retrato de estudio"})
    assert r.status_code == 400 and r.json["error"]["code"] == "sin_consentimiento"


def test_gemini_sin_clave_responde_claro(app, client):
    register(client)
    app.config["GEMINI_API_KEY"] = ""
    r = client.post("/api/v1/generations", json={"prompt": "retrato de estudio", "consent": True})
    assert r.status_code == 503 and "GEMINI_API_KEY" in r.json["error"]["message"]
    assert db.session.query(Generation).one().status == "failed"           # el intento queda registrado


def test_gemini_genera_y_guarda_en_la_galeria(app, client, monkeypatch):
    register(client)
    app.config["GEMINI_API_KEY"] = "clave-de-prueba"
    png = upload_bytes().getvalue()
    monkeypatch.setattr(gen_api, "generate_image", lambda prompt, key, model, timeout: (png, 1.5))
    r = client.post("/api/v1/generations", json={"prompt": "retrato de estudio, luz suave", "consent": True})
    assert r.status_code == 201
    image_id = r.json["data"]["image"]["id"]
    assert client.get(f"/api/v1/images/{image_id}/content").status_code == 200
    assert client.get("/api/v1/generations").json["data"][0]["image_id"] == image_id
    # La clave nunca vuelve al navegador
    assert "clave-de-prueba" not in client.get("/api/v1/generations/status").get_data(as_text=True)


def test_gemini_error_del_servicio(app, client, monkeypatch):
    register(client)
    app.config["GEMINI_API_KEY"] = "x"

    def boom(*_):
        raise GeminiError("gemini_limite")
    monkeypatch.setattr(gen_api, "generate_image", boom)
    r = client.post("/api/v1/generations", json={"prompt": "retrato de estudio", "consent": True})
    assert r.status_code == 429 and r.json["error"]["code"] == "gemini_limite"


def test_cliente_gemini_lee_la_imagen_de_la_respuesta(monkeypatch):
    """El cliente extrae inlineData de la respuesta REST sin usar la red."""
    import json
    from app.services import gemini_service
    payload = {"candidates": [{"content": {"parts": [{"text": "ok"},
               {"inlineData": {"mimeType": "image/png", "data": base64.b64encode(b"PNGDATA").decode()}}]}}]}

    class Resp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self, *args): return json.dumps(payload).encode()
    captured = {}

    def fake_urlopen(req, timeout):
        captured["key"] = req.headers.get("X-goog-api-key")
        return Resp()
    monkeypatch.setattr(gemini_service.urllib.request, "urlopen", fake_urlopen)
    data, _ = gemini_service.generate_image("hola mundo", "k-123", "gemini-2.5-flash-image")
    assert data == b"PNGDATA" and captured["key"] == "k-123"


@pytest.mark.parametrize("payload", [b"no-json", b"[]", b'{"candidates":[{"content":{"parts":[{"inlineData":{"data":"###"}}]}}]}'])
def test_respuesta_invalida_de_gemini_se_traduce_a_error_seguro(monkeypatch, payload):
    from app.services import gemini_service

    class Resp:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self, *args): return payload

    monkeypatch.setattr(gemini_service.urllib.request, "urlopen", lambda *args, **kwargs: Resp())
    with pytest.raises(GeminiError, match="gemini_servicio"):
        gemini_service.generate_image("prompt de prueba", "clave-que-no-debe-salir", "gemini-2.5-flash-image")
