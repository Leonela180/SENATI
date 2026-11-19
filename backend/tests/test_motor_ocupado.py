"""Si el motor está ocupado por otro trabajo, el trabajo espera su turno sin gastar intentos ni marcarse como fallido."""
from app.ai.interface import EngineError, HumanizationEngine, MockEngine
from app.extensions import db
from app.models import ProcessingJob, ServiceIncident
from app.workers import image_worker
from app.workers.image_worker import process_one
from tests.conftest import new_job, register, upload


class _BusyEngine(HumanizationEngine):
    def humanize(self, input_path, output_path, preset, seed=None, **kw):
        raise EngineError("motor_ocupado")


def test_motor_ocupado_no_consume_intentos(client, app, monkeypatch):
    monkeypatch.setattr(image_worker, "BUSY_WAIT_SECONDS", 0)
    register(client)
    image_id = upload(client).json["data"]["id"]
    job_id = new_job(client, image_id).json["data"]["id"]
    for _ in range(app.config["AI_MAX_ATTEMPTS"] + 2):                     # más esperas que intentos permitidos
        process_one(app, _BusyEngine())
    job = db.session.get(ProcessingJob, job_id)
    assert job.status == "queued" and job.attempt_count == 0 and job.error_code is None
    assert db.session.query(ServiceIncident).count() == 0
    process_one(app, MockEngine())                                          # cuando el motor se libera, se procesa
    job = db.session.get(ProcessingJob, job_id)
    assert job.status == "completed" and job.attempt_count == 1
