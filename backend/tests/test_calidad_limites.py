import numpy as np
from app.ai.editing import mejorar_calidad
from tests.conftest import register, upload


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
