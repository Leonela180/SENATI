"""La portada solo publica humanizaciones reales (nunca la simulación)."""
import importlib.util
import json
from pathlib import Path

import pytest
from PIL import Image

from app.extensions import db
from app.models import ProcessingJob
from app.storage.local_private import path_for
from app.workers.image_worker import process_one
from app.ai.interface import MockEngine
from tests.conftest import new_job, register, upload

SPEC = importlib.util.spec_from_file_location("preparar_portada", Path(__file__).parents[1] / "tools" / "preparar_portada.py")
portada = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(portada)


def _completed_job(app, client):
    register(client)
    job_id = new_job(client, upload(client).json["data"]["id"]).json["data"]["id"]
    process_one(app, MockEngine())
    return db.session.get(ProcessingJob, job_id)


def test_rechaza_resultados_de_simulacion(app, client, tmp_path):
    job = _completed_job(app, client)
    with pytest.raises(portada.PortadaError, match="SIMULACIÓN"):
        portada.demo_from_job(job, tmp_path, tmp_path / "demo")
    assert not (tmp_path / "demo").exists()


def test_publica_un_resultado_real_con_procedencia(app, client, tmp_path):
    job = _completed_job(app, client)
    job.model_id, job.parameters = "stable-diffusion-v1-5:sd15-q4_0", {**job.parameters, "seconds": 156.08, "device": "cpu"}
    demo = portada.demo_from_job(job, tmp_path, tmp_path / "demo")
    saved = json.loads((tmp_path / "demo" / "demo.json").read_text(encoding="utf-8"))
    assert saved == demo and "No es una fotografía de una persona real" in demo["caption"]
    with Image.open(tmp_path / "demo" / "antes.webp") as a, Image.open(tmp_path / "demo" / "despues.webp") as b:
        assert a.size == b.size
