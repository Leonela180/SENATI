import numpy as np
from app.ai.editing import mejorar_calidad
from tests.conftest import register, upload
import cv2


def test_calidad_sin_ajustes_no_cambia_tonos_ni_contraste():
    rng = np.random.default_rng(42)
    image = rng.integers(20, 220, (80, 90, 3), dtype=np.uint8)
    assert np.array_equal(mejorar_calidad(image, 1, 0, False), image)


def test_enfoque_no_produce_halos_fuertes_ni_cambia_canales():
    image = np.full((32, 32, 3), (65, 85, 105), dtype=np.uint8)
    image[:, 16:] = (155, 175, 195)
    base = cv2.resize(image, (128, 128), interpolation=cv2.INTER_CUBIC)
    output = mejorar_calidad(image, 4, 2, False)
    delta = output.astype(int)-base.astype(int)
    assert np.abs(delta).max() <= 3
    assert np.array_equal(delta[..., 0], delta[..., 1])
    assert np.array_equal(delta[..., 1], delta[..., 2])


def test_calidad_limita_salida_a_4096():
    image = np.full((4, 4200, 3), 180, dtype=np.uint8)
    result = mejorar_calidad(image, 4, 0, False)
    assert result.shape[1] == 4096


def test_escala_cuatro_y_rechazo_de_fracciones(client):
    register(client)
    image_id = upload(client).json["data"]["id"]
    def create(scale):
        return client.post("/api/v1/jobs", json={"image_id": image_id, "tool": "mejorar_calidad", "params": {"scale": scale}}, headers={"Idempotency-Key": f"escala-prueba-{scale}"})
    assert create(4).status_code == 201
    assert create(1.5).status_code == 400
