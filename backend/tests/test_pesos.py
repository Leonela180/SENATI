import numpy as np
import pytest

# safetensors llega con el motor de IA (instalar.ps1 sin -SinIA); sin él, estas pruebas se omiten
safetensors_numpy = pytest.importorskip("safetensors.numpy", reason="Motor de IA no instalado (-SinIA)")
load_file, save_file = safetensors_numpy.load_file, safetensors_numpy.save_file
from app.ai import weights


def test_conversion_por_bloques_conserva_formas_enteros_y_original(tmp_path, monkeypatch):
    source, output = tmp_path / "source.safetensors", tmp_path / "half.safetensors"
    save_file({"weights": np.array([[1.25, -0.5], [0, 2]], dtype=np.float32),
               "counter": np.array([1234], dtype=np.int64)}, source)
    original_bytes = source.read_bytes()
    monkeypatch.setattr(weights, "available_ram_gib", lambda: 3.0)
    weights.compact_safetensors(source, output)
    converted = load_file(output)
    assert converted["weights"].dtype == np.float16
    np.testing.assert_array_equal(converted["weights"], [[1.25, -0.5], [0, 2]])
    assert converted["counter"].dtype == np.int64
    assert converted["counter"].tolist() == [1234]
    assert source.read_bytes() == original_bytes
    with pytest.raises(ValueError, match="existe"):
        weights.compact_safetensors(source, output)
