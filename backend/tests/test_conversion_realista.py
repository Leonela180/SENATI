from PIL import Image
from tests.conftest import register, upload
from tests.test_motor_ligero import make_engine
from app.ai import lite_engine


def test_conversion_no_reaplica_dibujo_ni_mezcla_original(tmp_path, monkeypatch):
    engine = make_engine(tmp_path)
    source, result = tmp_path / "dibujo.png", tmp_path / "resultado.png"
    Image.new("RGB", (384, 384), "tan").save(source)
    stages = []
    def safety(image, directory, stage):
        stages.append(stage)
        return {"ram_free_min_gib": 2.5}
    def inference(command, *args, **kwargs):
        assert command[command.index("--strength") + 1] == "0.78"
        Image.new("RGB", (384, 384), "red").save(command[command.index("--output") + 1])
        return {"ram_free_min_gib": 2.2}
    monkeypatch.setattr(engine, "check_safety", safety)
    monkeypatch.setattr(lite_engine, "run_limited", inference)
    monkeypatch.setattr(lite_engine, "enhance_facial_detail", lambda *a: (_ for _ in ()).throw(AssertionError("No copiar rasgos cartoon al resultado")))
    metadata = engine.humanize(source, result, "natural", mode="realista")
    assert stages == ["input", "output"] and metadata["blend"] == 1.0
    assert Image.open(result).getpixel((0, 0)) == (255, 0, 0)
    assert metadata["conversion_mode"] == "ilustracion_a_realista"


def test_conversion_exige_motor_real_y_respeta_idempotencia(app, client, tmp_path):
    register(client)
    image_id = upload(client).json["data"]["id"]
    headers = {"Idempotency-Key": "conversion-probar-001"}
    body = {"tool": "realista", "image_id": image_id}
    assert client.post("/api/v1/jobs", json=body, headers=headers).status_code == 503
    model = tmp_path / "compact.safetensors"
    app.config.update(AI_ENGINE="local", AI_LOCAL_RUNTIME="cpp", AI_REALISTIC_ENABLED=True, AI_REALISTIC_MODEL_PATH=model)
    assert client.post("/api/v1/jobs", json=body, headers=headers).status_code == 503
    model.write_bytes(b"fixture")
    assert client.post("/api/v1/jobs", json={**body, "params": {"character": "otro"}}, headers=headers).status_code == 400
    first = client.post("/api/v1/jobs", json=body, headers=headers)
    assert first.status_code == 201
    second = client.post("/api/v1/jobs", json=body, headers=headers)
    assert second.status_code == 200 and second.json["data"]["id"] == first.json["data"]["id"]
