from app.extensions import db
from app.models import ProcessingJob
from app.workers.image_worker import process_one
from tests.conftest import register, upload


def test_repetir_conserva_herramienta_y_puntos_privados(client, other_client, app):
    register(client)
    image_id = upload(client).json["data"]["id"]
    body = {"image_id": image_id, "tool": "quitar_lunar", "params": {"points": [{"x": 20, "y": 25, "r": 4}]}}
    first = client.post("/api/v1/jobs", json=body, headers={"Idempotency-Key": "retoque-original-001"}).json["data"]
    headers = {"Idempotency-Key": "retoque-repetido-001"}
    path = f"/api/v1/jobs/{first['id']}/retry"
    assert client.post(path, headers=headers).status_code == 409
    process_one(app, None)
    repeated = client.post(path, headers=headers)
    assert repeated.status_code == 201
    job = db.session.get(ProcessingJob, repeated.json["data"]["id"])
    assert job.tool == "quitar_lunar" and job.parameters["points"] == body["params"]["points"]
    assert "points" not in repeated.json["data"]["parameters"]
    assert client.post(path, headers=headers).json["data"]["id"] == job.id
    register(other_client, "otro@demo.pe")
    assert other_client.post(path, headers={"Idempotency-Key": "intento-ajeno-001"}).status_code == 404
