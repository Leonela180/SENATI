"""Estudio de edición (CPU): quitar lunar, cambiar fondo, desenfoque, mejorar calidad y ajustes."""
import io

import numpy as np
import pytest
from PIL import Image as PILImage

from app.ai import editing
from app.extensions import db
from app.models import ProcessingJob
from app.workers.image_worker import process_one
from tests.conftest import register, upload


@pytest.fixture(autouse=True)
def fake_segmentation(monkeypatch):
    """La segmentación real usa un modelo descargable; en las pruebas se usa una máscara fija (persona al centro)."""
    def alpha(rgb):
        h, w = rgb.shape[:2]
        a = np.zeros((h, w), np.float32)
        a[h // 4: 3 * h // 4, w // 4: 3 * w // 4] = 1.0
        return a
    monkeypatch.setattr(editing, "_person_alpha", alpha)


def _job(client, image_id, tool, params, key):
    return client.post("/api/v1/jobs", json={"image_id": image_id, "tool": tool, "params": params},
                       headers={"Idempotency-Key": key})


def _result(app, client, job_id):
    process_one(app, None)                         # sin motor de IA: las herramientas del Estudio igual funcionan
    job = db.session.get(ProcessingJob, job_id)
    assert job.status == "completed", job.error_code
    r = client.get(f"/api/v1/jobs/{job_id}/download")
    assert r.status_code == 200
    return job, PILImage.open(io.BytesIO(r.data)), r.data


def test_quitar_lunar_rellena_solo_la_zona_marcada(app, client):
    register(client)
    buf = io.BytesIO()
    img = PILImage.new("RGB", (120, 120), (200, 160, 130))
    img.putpixel((60, 60), (40, 20, 10))
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            img.putpixel((60 + dx, 60 + dy), (40, 20, 10))        # «lunar» oscuro
    img.save(buf, "PNG"); buf.seek(0)
    image_id = client.post("/api/v1/images", data={"file": (buf, "lunar.png"), "declaracion_ia": "true"},
                           content_type="multipart/form-data").json["data"]["id"]
    r = _job(client, image_id, "quitar_lunar", {"points": [{"x": 60, "y": 60, "r": 8}]}, "lunar-0001")
    assert r.status_code == 201 and r.json["data"]["tool"] == "quitar_lunar"
    job, out, raw = _result(app, client, r.json["data"]["id"])
    px = np.asarray(out.convert("RGB")).astype(int)
    assert abs(px[60, 60] - np.array([200, 160, 130])).max() < 25          # el lunar desapareció
    assert (px[5, 5] == [200, 160, 130]).all()                             # lejos del punto no cambia nada
    assert b"LUMIA AI" in raw and job.parameters["puntos"] == 1


def test_cambiar_fondo_color_y_transparente(app, client):
    register(client)
    image_id = upload(client, size=(80, 80)).json["data"]["id"]
    r = _job(client, image_id, "cambiar_fondo", {"mode": "color", "color": "#00ff00"}, "fondo-0001")
    _, out, raw = _result(app, client, r.json["data"]["id"])
    assert out.convert("RGB").getpixel((2, 2)) == (0, 255, 0)              # fondo nuevo
    assert b"editado con IA" in raw                                        # la segmentación es un modelo de IA
    r = _job(client, image_id, "cambiar_fondo", {"mode": "transparente"}, "fondo-0002")
    _, out, _ = _result(app, client, r.json["data"]["id"])
    assert out.mode == "RGBA" and out.getpixel((2, 2))[3] == 0 and out.getpixel((40, 40))[3] == 255


def test_desenfoque_y_mejorar_calidad(app, client):
    register(client)
    image_id = upload(client, size=(64, 48)).json["data"]["id"]
    r = _job(client, image_id, "desenfoque", {"radius": 4, "scope": "fondo"}, "blur-00001")
    assert _result(app, client, r.json["data"]["id"])[1].size == (64, 48)
    r = _job(client, image_id, "mejorar_calidad", {"scale": 2, "sharpen": 0.8, "denoise": True}, "calidad-001")
    job, out, _ = _result(app, client, r.json["data"]["id"])
    assert out.size == (128, 96) and job.parameters["width"] == 128        # escalado ×2 registrado
    r = _job(client, image_id, "ajustes", {"brightness": 1.2, "rotate": 90}, "ajustes-001")
    assert _result(app, client, r.json["data"]["id"])[1].size == (48, 64)  # rotación de 90°


@pytest.mark.parametrize("tool,params", [
    ("quitar_lunar", {"points": []}),
    ("quitar_lunar", {"points": [{"x": 9999, "y": 1, "r": 5}]}),
    ("cambiar_fondo", {"mode": "lila"}),
    ("cambiar_fondo", {"mode": "color", "color": "verde"}),
    ("desenfoque", {"radius": 500}),
    ("mejorar_calidad", {"scale": 8}),
    ("ajustes", {"rotate": 45}),
])
def test_parametros_invalidos_se_rechazan(client, tool, params):
    register(client)
    image_id = upload(client).json["data"]["id"]
    r = _job(client, image_id, tool, params, f"inval-{tool}")
    assert r.status_code == 400 and r.json["error"]["code"] == "parametros_invalidos"


def test_no_se_edita_una_imagen_ajena(client, other_client):
    register(client)
    image_id = upload(client).json["data"]["id"]
    register(other_client, "b@demo.pe")
    r = _job(other_client, image_id, "desenfoque", {"radius": 3}, "ajena-0001")
    assert r.status_code == 404


def test_guardar_resultado_como_imagen_para_encadenar(app, client):
    register(client)
    image_id = upload(client).json["data"]["id"]
    job_id = _job(client, image_id, "ajustes", {"brightness": 1.1}, "cadena-001").json["data"]["id"]
    assert client.post(f"/api/v1/jobs/{job_id}/save").status_code == 409            # aún en cola
    process_one(app, None)
    r = client.post(f"/api/v1/jobs/{job_id}/save")
    assert r.status_code == 201 and r.json["data"]["filename"].endswith("_ajustes.png")
    assert client.get("/api/v1/images").json["data"]["total"] == 2
