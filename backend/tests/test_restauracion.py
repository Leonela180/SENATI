import io
import hashlib
import numpy as np
import pytest
from PIL import Image
from app.ai.editing import restaurar
from tests.conftest import register
from tests.test_estudio import _job, _result


def test_restauracion_repara_dano_y_conserva_original(app, client):
    register(client)
    rgb = np.full((96, 96, 3), 150, dtype=np.uint8)
    rgb[40:57, 48:51] = 255
    buffer = io.BytesIO()
    Image.fromarray(rgb).save(buffer, 'PNG')
    original_hash = hashlib.sha256(buffer.getvalue()).hexdigest()
    buffer.seek(0)
    image_id = client.post('/api/v1/images', data={'file': (buffer, 'recuerdo.png'), 'declaracion_ia': 'true'}, content_type='multipart/form-data').json['data']['id']
    response = _job(client, image_id, 'restaurar', {'intensity': 0.5, 'points': [{'x': 49, 'y': 48, 'r': 12}]}, 'restaurar-001')
    assert response.status_code == 201
    job, out, raw = _result(app, client, response.json['data']['id'])
    assert out.size == (96, 96) and out.getpixel((49, 48))[0] < 200
    assert job.parameters['intensity'] == 0.5 and b'LUMIA AI' in raw
    original = client.get(f'/api/v1/images/{image_id}/content')
    assert hashlib.sha256(original.data).hexdigest() == original_hash


def test_restauracion_sin_puntos_no_inventa_color():
    grey = np.tile(np.linspace(80, 170, 80).astype(np.uint8), (80, 1))
    out = restaurar(np.dstack([grey] * 3), 0.6, [])
    assert out.shape == (80, 80, 3)
    assert np.abs(out[..., 0].astype(int) - out[..., 2].astype(int)).max() < 5


@pytest.mark.parametrize('params', [{'intensity': 2}, {'points': [{'x': -1, 'y': 1, 'r': 4}]}, {'points': 'bad'}])
def test_restauracion_rechaza_parametros(client, params):
    from tests.conftest import upload
    register(client)
    image_id = upload(client).json['data']['id']
    assert _job(client, image_id, 'restaurar', params, 'restaurar-invalid').status_code == 400
