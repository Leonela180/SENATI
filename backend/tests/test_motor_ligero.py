import json
import pytest
from PIL import Image
from app.ai import lite_engine, processes
from app.ai.interface import EngineError


@pytest.mark.parametrize("size", [(1254, 1254), (1000, 600), (70, 2000), (64, 64)])
def test_preparacion_limita_resolucion_y_conserva_proporcion(size):
    original = Image.new("RGB", size, "tan")
    work, crop = lite_engine.prepare_image(original, 384)
    assert max(work.size) <= 384
    assert all(side % 64 == 0 for side in work.size)
    content = work.crop(crop)
    assert abs(content.width / content.height - size[0] / size[1]) <= 0.02
    assert original.size == size


def test_solo_un_motor_ligero_puede_procesar(tmp_path):
    path = tmp_path / "motor.lock"
    with lite_engine.exclusive_inference(path):
        with pytest.raises(EngineError, match="motor_ocupado"):
            with lite_engine.exclusive_inference(path):
                pytest.fail("Dos motores entraron al mismo tiempo")
    with lite_engine.exclusive_inference(path):
        pass


def make_engine(tmp_path):
    executable = tmp_path / "sd-cli.exe"
    executable.write_bytes(b"test")
    model = tmp_path / "model.gguf"
    model.write_bytes(b"GGUF")
    safety = tmp_path / "safety_checker/model.fp16.safetensors"
    safety.parent.mkdir()
    safety.touch()
    return lite_engine.LiteHumanizationEngine(executable, model, tmp_path, tmp_path / "scratch")


def test_no_publica_resultado_si_el_filtro_de_salida_lo_rechaza(tmp_path, monkeypatch):
    engine = make_engine(tmp_path)
    source, output = tmp_path / "original.png", tmp_path / "publicado.png"
    Image.new("RGB", (384, 384), "tan").save(source)
    calls = []

    def safety(image, directory, stage):
        calls.append(stage)
        if stage == "output":
            raise EngineError("contenido_bloqueado")
        return {"ram_free_min_gib": 2.5}

    def inference(command, *args, **kwargs):
        raw = command[command.index("--output") + 1]
        Image.new("RGB", (384, 384), "white").save(raw)
        return {"ram_free_min_gib": 2.2}

    monkeypatch.setattr(engine, "check_safety", safety)
    monkeypatch.setattr(lite_engine, "run_limited", inference)
    with pytest.raises(EngineError, match="contenido_bloqueado"):
        engine.humanize(source, output, "natural")
    assert calls == ["input", "output"]
    assert not output.exists()
    assert Image.open(source).getpixel((0, 0)) == (210, 180, 140)


def test_no_arranca_proceso_sin_memoria(tmp_path, monkeypatch):
    monkeypatch.setattr(processes, "available_ram_gib", lambda: 0.9)
    monkeypatch.setattr(processes.subprocess, "Popen", lambda *args, **kwargs: pytest.fail("Arrancó sin recursos"))
    with pytest.raises(EngineError, match="memoria_insuficiente"):
        processes.run_limited(["inferencia"], tmp_path / "log.txt")


def test_respuesta_incompleta_del_filtro_se_rechaza(tmp_path, monkeypatch):
    engine = make_engine(tmp_path)
    monkeypatch.setattr(lite_engine, "run_limited", lambda *args, **kwargs: {"ram_free_min_gib": 2.5})
    (tmp_path / "safety_input.json").write_text(json.dumps({}), encoding="utf-8")
    with pytest.raises(EngineError, match="filtro_no_disponible"):
        engine.check_safety(tmp_path / "image.png", tmp_path, "input")


def test_baja_memoria_detiene_solo_el_proceso_creado(tmp_path, monkeypatch):
    readings = iter([3.0, 0.5])
    monkeypatch.setattr(processes, "available_ram_gib", lambda: next(readings))
    killed = []

    class Process:
        pid, returncode = 12345, None
        def poll(self): return self.returncode
        def wait(self, timeout):
            self.returncode = -15
            return self.returncode
        def terminate(self): killed.append(self.pid)

    process = Process()
    monkeypatch.setattr(processes.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(processes.subprocess, "run", lambda args, **kwargs: killed.append(args))
    with pytest.raises(EngineError, match="memoria_insuficiente"):
        processes.run_limited(["inferencia"], tmp_path / "proceso.log")
    assert process.returncode == -15
    if processes.os.name == "nt":
        assert killed == [["taskkill", "/PID", "12345", "/T", "/F"]]
    else:
        assert killed == [12345]


def test_runtime_ligero_ofrece_solo_el_preset_validado(app, client):
    from tests.conftest import register, upload
    app.config.update(AI_ENGINE="local", AI_LOCAL_RUNTIME="cpp")
    assert client.get("/api/v1/health").json["data"]["presets"] == ["natural"]
    register(client)
    image_id = upload(client).json["data"]["id"]
    response = client.post("/api/v1/jobs", json={"image_id": image_id, "preset": "fotografico"},
                           headers={"Idempotency-Key": "prueba-preset-ligero"})
    assert response.json["data"]["preset"] == "natural"
