import numpy as np
from PIL import Image
from app.ai import facial_detail


def fixture_portrait():
    image = np.full((400, 400, 3), (190, 145, 115), dtype=np.uint8)
    image[110:125, 140:155] = (20, 20, 20)
    image[112:116, 145:149] = (205, 205, 205)
    return Image.fromarray(image)


def test_textura_reproducible_sin_editar_fondo_ni_pupila(tmp_path, monkeypatch):
    original = fixture_portrait()
    generated = Image.new("RGB", original.size, (185, 140, 110))
    monkeypatch.setattr(facial_detail, "detect_regions", lambda image: ((60, 40, 280, 320), [(115, 85, 75, 60)]))
    result, metadata = facial_detail.enhance_facial_detail(original, generated)
    repeat, _ = facial_detail.enhance_facial_detail(original, generated)
    np.testing.assert_array_equal(result, repeat)
    assert metadata["facial_detail_applied"] is True
    assert metadata["eyes_enhanced"] == 1
    before, after = np.asarray(original), np.asarray(result)
    np.testing.assert_array_equal(after[:40], before[:40])
    np.testing.assert_array_equal(after[:, :60], before[:, :60])
    np.testing.assert_array_equal(after[120, 150], before[120, 150])
    assert np.any(after != before)


def test_sin_rostro_no_inventa_mascaras(monkeypatch):
    original = fixture_portrait()
    generated = Image.new("RGB", original.size, "tan")
    monkeypatch.setattr(facial_detail, "detect_regions", lambda image: (None, []))
    result, metadata = facial_detail.enhance_facial_detail(original, generated)
    np.testing.assert_array_equal(result, generated)
    assert metadata["facial_detail_applied"] is False
    assert metadata["eyes_enhanced"] == 0


def test_intensidad_cero_reproduce_original():
    original = fixture_portrait()
    result, _ = facial_detail.enhance_facial_detail(original, Image.new("RGB", original.size), intensity=0)
    np.testing.assert_array_equal(result, original)
