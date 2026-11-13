from app.ai.interface import HumanizationEngine, MockEngine
from app.extensions import db
from app.models import AuditEvent, ProcessingJob, ServiceIncident
from app.workers.image_worker import CLAIM_SQL, process_one
from tests.conftest import new_job, register, upload


def _job(client):
    register(client)
    image_id = upload(client).json["data"]["id"]
    return new_job(client, image_id).json["data"]["id"]


def test_cp07_idempotencia(client):
    register(client)
    image_id = upload(client).json["data"]["id"]
    r1 = new_job(client, image_id)
    r2 = new_job(client, image_id)
    assert r1.status_code == 201 and r2.status_code == 200
    assert r1.json["data"]["id"] == r2.json["data"]["id"]
    assert db.session.query(ProcessingJob).count() == 1


def test_cp08_dos_workers(client):
    _job(client)
    c1, c2 = db.engine.connect(), db.engine.connect()
    t1, t2 = c1.begin(), c2.begin()
    r1 = c1.execute(CLAIM_SQL).first()
    r2 = c2.execute(CLAIM_SQL).first()                                         # SKIP LOCKED: no lo ve
    t1.commit(); t2.commit(); c1.close(); c2.close()
    assert r1 is not None and r2 is None


def test_cp09_fallo_del_motor(client, app):
    job_id = _job(client)
    for _ in range(app.config["AI_MAX_ATTEMPTS"]):
        process_one(app, None)                                                 # motor sin pesos
    job = db.session.get(ProcessingJob, job_id)
    assert job.status == "failed" and job.error_code == "modelo_no_disponible"
    assert db.session.query(ServiceIncident).count() == 1
    assert "Traceback" not in client.get(f"/api/v1/jobs/{job_id}").get_data(as_text=True)


class _NoFileEngine(HumanizationEngine):
    def humanize(self, input_path, output_path, preset, seed=None):
        return {"model_id": "x", "model_version": "x"}                         # «olvida» guardar el archivo


def test_rnf07_completed_solo_con_archivo(client, app):
    job_id = _job(client)
    for _ in range(app.config["AI_MAX_ATTEMPTS"]):
        process_one(app, _NoFileEngine())
    job = db.session.get(ProcessingJob, job_id)
    assert job.status == "failed" and job.error_code == "resultado_inexistente"


def test_cp11_acceso_cruzado(client, other_client, app):
    job_id = _job(client)
    process_one(app, MockEngine())
    register(other_client, "b@demo.pe")
    image_id = db.session.get(ProcessingJob, job_id).image_id
    assert other_client.get(f"/api/v1/jobs/{job_id}").status_code == 404
    assert other_client.get(f"/api/v1/jobs/{job_id}/download").status_code == 404
    assert other_client.get(f"/api/v1/images/{image_id}/content").status_code == 404


def test_cp12_descarga_autorizada(client, app):
    job_id = _job(client)
    process_one(app, MockEngine())
    r = client.get(f"/api/v1/jobs/{job_id}/download")
    assert r.status_code == 200
    assert "editado_IA" in r.headers["Content-Disposition"]                    # RF-16: en el nombre
    assert b"editado con IA" in r.data                                         # RF-16: en los metadatos
    assert db.session.query(AuditEvent).filter_by(action="job.download", entity_id=job_id).count() == 1


def test_rnf10_trazabilidad(client, app):
    job_id = _job(client)
    process_one(app, MockEngine())
    data = client.get(f"/api/v1/jobs/{job_id}").json["data"]
    assert data["status"] == "completed" and data["model_id"] == "mock"
    assert {"strength", "steps", "guidance", "seed"} <= set(data["parameters"])
