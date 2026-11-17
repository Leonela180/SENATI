import pytest
from app.ai import resources
from app.ai.interface import EngineError


def test_no_carga_modelo_pesado_con_memoria_insuficiente(monkeypatch):
    monkeypatch.setattr(resources, "available_ram_gib", lambda: 1.77)
    with pytest.raises(EngineError, match="memoria_insuficiente"):
        resources.require_memory()


def test_permite_validacion_si_hay_memoria_disponible(monkeypatch):
    monkeypatch.setattr(resources, "available_ram_gib", lambda: 8.0)
    assert resources.require_memory() == 8.0
