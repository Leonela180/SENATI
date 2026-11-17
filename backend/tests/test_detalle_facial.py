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


def _portrait_with_gradient(size=400):
    """Retrato sintético con luz lateral (degradado), como un rostro real con sombras."""
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    base = np.stack([190 - xx * .08, 145 - xx * .06, 115 - xx * .05], axis=-1)
    rng = np.random.default_rng(7)
    base += rng.normal(0, 2.5, base.shape)                     # grano fino, como una foto
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))


def test_sin_efecto_mascarilla_aunque_la_ia_cambie_el_tono(monkeypatch):
    """Regresión del resultado lumia_10: la cara no debe cambiar de tono respecto del cuello ni dejar costuras."""
    original = _portrait_with_gradient()
    shifted = np.asarray(original, dtype=np.int16) + np.array([14, 9, 6])     # la IA aclara/calienta todo
    generated = Image.fromarray(np.clip(shifted, 0, 255).astype(np.uint8))
    monkeypatch.setattr(facial_detail, "detect_regions", lambda image: ((60, 40, 280, 320), [(115, 85, 75, 60)]))
    result, metadata = facial_detail.enhance_facial_detail(original, generated)
    assert metadata["facial_detail_applied"] is True
    before, after = np.asarray(original, np.float32), np.asarray(result, np.float32)
    change = (after - before).mean(axis=2)
    # 1) Sin cambio de tono en el rostro: el promedio del cambio en la cara es casi cero
    assert abs(change[120:300, 120:280].mean()) < 1.0
    # 2) Sin costuras en el borde del recuadro del rostro
    assert np.abs(change[40:360, 58:62]).max() < 1.5 and np.abs(change[38:42, 60:340]).max() < 1.5
    # 3) Sin parches: el cambio a baja frecuencia es suave (ningún salto brusco entre zonas vecinas)
    import cv2
    low = cv2.GaussianBlur(change, (0, 0), 6)
    assert np.abs(np.diff(low, axis=0)).max() < 0.6 and np.abs(np.diff(low, axis=1)).max() < 0.6
