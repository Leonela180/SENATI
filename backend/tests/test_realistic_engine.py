from pathlib import Path
from types import SimpleNamespace
import pytest
from PIL import Image
from app.ai import realistic_engine
from app.ai.interface import EngineError
from app.ai.realistic_engine import RealisticEngine


@pytest.mark.parametrize("blocked", [False, True])
def test_conversion_filtra_antes_de_publicar_y_limpia_temporales(tmp_path, monkeypatch, blocked):
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    model = tmp_path / "compact.safetensors"
    model.write_bytes(b"fixture")
    source, output = tmp_path / "source.png", tmp_path / "output.png"
    Image.new("RGB", (640, 640), "tan").save(source)
    stages = []

    def safety(path, directory, stage):
        stages.append(stage)
        assert not output.exists()
        if stage == "output" and blocked:
            raise EngineError("contenido_bloqueado")
        return {"ram_free_min_gib": 2.0}

    def inference(command, *args, **kwargs):
        assert stages == ["input"]
        Image.new("RGB", (512, 512), "red").save(command[command.index("--output")+1])
        (Path(command[command.index("--output")+1]).parent / "offload").mkdir()
        return {"ram_free_min_gib": 1.2}

    monkeypatch.setattr(realistic_engine, "run_limited", inference)
    checker = SimpleNamespace(scratch=scratch, models_dir=tmp_path, check_safety=safety)
    engine = RealisticEngine(checker, model)
    if blocked:
        with pytest.raises(EngineError, match="contenido_bloqueado"):
            engine.humanize(source, output)
        assert not output.exists()
    else:
        metadata = engine.humanize(source, output)
        assert Image.open(output).size == (512, 512)
        assert Image.open(output).getpixel((0, 0)) == (255, 0, 0)
        assert metadata["runtime"] == "diffusers_disk_offload"
        assert metadata["filtro_seguridad"] is True
    assert stages == ["input", "output"]
    assert not list(scratch.glob("job_*"))
