"""«Textura de piel realista»: solo cambia la piel detectada, protege rasgos y rechaza imágenes sin rostro."""
import io

import cv2
import numpy as np
import pytest
from PIL import Image as PILImage

from app.ai import facial_detail, skin_texture
from app.ai.interface import EngineError
from app.extensions import db
from app.models import ProcessingJob
from app.workers.image_worker import process_one
from tests.conftest import register

FACE = (100, 80, 200, 200)                      # x, y, ancho, alto del rostro sintético


def _retrato():
    """Retrato sintético «de plástico»: fondo gris, cara color piel totalmente lisa, ojos y boca oscuros."""
    img = np.full((420, 400, 3), (120, 125, 130), np.uint8)
    cv2.ellipse(img, (200, 190), (95, 120), 0, 0, 360, (214, 170, 144), -1)
    for cx in (155, 245):
        cv2.ellipse(img, (cx, 150), (18, 9), 0, 0, 360, (40, 30, 30), -1)
    cv2.ellipse(img, (200, 245), (34, 10), 0, 0, 360, (150, 60, 70), -1)
    return img


@pytest.fixture
def cara_detectada(monkeypatch):
    eyes = [(137, 141, 36, 18), (227, 141, 36, 18)]
    monkeypatch.setattr(skin_texture, "detect_regions", lambda image: (FACE, eyes))


def test_agrega_textura_solo_en_la_piel(cara_detectada):
    rgb = _retrato()
    out, meta = skin_texture.textura_piel(rgb, 0.8)
    diff = np.abs(out.astype(int) - rgb).sum(axis=2)
    mejilla = (slice(185, 215), slice(130, 160))
    gris = lambda a: cv2.cvtColor(a, cv2.COLOR_RGB2GRAY)[mejilla].astype(float)
    assert gris(rgb).std() < 0.5 < 1.5 < gris(out).std()                                # ya no es lisa
    assert diff[:40].max() == 0 and diff[:, :40].max() == 0                             # el fondo no cambia
    assert diff[147:153, 150:160].max() <= 2                                            # centro del ojo intacto
    assert abs(out[mejilla].mean() - rgb[mejilla].mean()) < 3                           # no cambia el tono
    assert meta["rostro_detectado"] and meta["ojos_protegidos"] == 2


def test_intensidad_y_pecas_cambian_el_resultado(cara_detectada):
    rgb = _retrato()
    suave, _ = skin_texture.textura_piel(rgb, 0.3)
    fuerte, _ = skin_texture.textura_piel(rgb, 1.0)
    pecas, _ = skin_texture.textura_piel(rgb, 1.0, freckles=True)
    d = lambda a: np.abs(a.astype(int) - rgb).mean()
    assert d(suave) < d(fuerte) < d(pecas)
    again, _ = skin_texture.textura_piel(rgb, 1.0)
    assert (again == fuerte).all()                                                      # reproducible


def test_sin_rostro_da_error_claro(monkeypatch):
    monkeypatch.setattr(skin_texture, "detect_regions", lambda image: (None, []))
    with pytest.raises(EngineError) as error:
        skin_texture.textura_piel(_retrato(), 0.7)
    assert error.value.code == "sin_rostro"


def test_estudio_textura_piel_de_punta_a_punta(app, client, cara_detectada):
    register(client)
    buf = io.BytesIO()
    PILImage.fromarray(_retrato()).save(buf, "PNG"); buf.seek(0)
    image_id = client.post("/api/v1/images", data={"file": (buf, "retrato.png"), "declaracion_ia": "true"},
                           content_type="multipart/form-data").json["data"]["id"]
    bad = client.post("/api/v1/jobs", json={"image_id": image_id, "tool": "textura_piel", "params": {"intensity": 3}},
                      headers={"Idempotency-Key": "piel-0000"})
    assert bad.status_code == 400
    r = client.post("/api/v1/jobs", json={"image_id": image_id, "tool": "textura_piel",
                                          "params": {"intensity": 0.7, "pecas": True}},
                    headers={"Idempotency-Key": "piel-0001"})
    assert r.status_code == 201 and r.json["data"]["tool_label"] == "Textura de piel realista"
    process_one(app, None)
    job = db.session.get(ProcessingJob, r.json["data"]["id"])
    assert job.status == "completed", job.error_code
    assert job.parameters["pecas"] is True and job.parameters["rostro_detectado"] is True
    raw = client.get(f"/api/v1/jobs/{job.id}/download").data
    assert b"LUMIA AI" in raw


def test_estudio_textura_sin_rostro_falla_con_mensaje(app, client, monkeypatch):
    monkeypatch.setattr(skin_texture, "detect_regions", lambda image: (None, []))
    register(client)
    buf = io.BytesIO()
    PILImage.new("RGB", (200, 200), (90, 140, 200)).save(buf, "PNG"); buf.seek(0)
    image_id = client.post("/api/v1/images", data={"file": (buf, "cielo.png"), "declaracion_ia": "true"},
                           content_type="multipart/form-data").json["data"]["id"]
    r = client.post("/api/v1/jobs", json={"image_id": image_id, "tool": "textura_piel", "params": {"intensity": 0.7}},
                    headers={"Idempotency-Key": "piel-0002"})
    process_one(app, None)
    job = client.get(f"/api/v1/jobs/{r.json['data']['id']}").json["data"]
    assert job["status"] == "failed" and "rostro" in job["error_message"]


def test_deteccion_real_no_inventa_rostros():
    """Con el detector real (sin simular), una imagen sin cara no se procesa."""
    assert facial_detail.detect_regions(PILImage.new("RGB", (300, 300), (200, 170, 150)))[0] is None
