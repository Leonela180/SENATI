"""Trabajo real de conversión en una cuenta DEMO; no habilita el laboratorio público."""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from app.config import ROOT
from app.extensions import db
from app.models import ProcessingJob
from app.workers.image_worker import build_engine, process_one
from preparar_cuentas_demo import call


def main():
    folder = ROOT / "private_data/demo_senati"
    state = json.loads((folder / "accesos_y_avance.json").read_text(encoding="utf-8"))
    account = state["accounts"]["individual1"]
    report_file = folder / "conversion-real-hombre.json"
    report = json.loads(report_file.read_text(encoding="utf-8")) if report_file.exists() else {}
    app = create_app(WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False, AI_REALISTIC_ENABLED=True)
    with app.app_context():
        if app.config["AI_ENGINE"] != "local" or app.config["AI_LOCAL_RUNTIME"] != "cpp":
            raise RuntimeError("La validacion exige el motor real local compatible.")
        if db.session.query(ProcessingJob).filter(ProcessingJob.status.in_(["queued", "processing"])).count():
            raise RuntimeError("Existen trabajos activos; no interferir.")
        client = app.test_client()
        call(client, "POST", "/auth/login", json={"email": account["email"], "password": account["password"]})
        if not report.get("image_id"):
            with (folder / "ilustracion.png").open("rb") as source:
                image = call(client, "POST", "/images", data={"file": (source, "DEMO_personaje_adulto.png"),
                    "permiso_edicion": "true", "album_id": str(account["albums"]["01 · Originales DEMO"])}, content_type="multipart/form-data")
            report["image_id"] = image["id"]
        job = call(client, "POST", "/jobs", json={"image_id": report["image_id"], "tool": "realista", "params": {"character": "adult_man"}},
                   headers={"Idempotency-Key": "demo-realista-offload-hombre-v2"})
        report["job_id"] = job["id"]
        report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
        if job["status"] == "queued":
            process_one(app, build_engine(app))
        job = call(client, "GET", f"/jobs/{job['id']}")
        report.update(status=job["status"], parameters=job["parameters"], error_code=job["error_code"], visual_review="pendiente")
        if job["status"] == "completed":
            download = client.get(f"/api/v1/jobs/{job['id']}/download")
            assert download.status_code == 200
            (folder / "conversion-real-hombre.png").write_bytes(download.data)
            if not report.get("saved_image_id"):
                saved = call(client, "POST", f"/jobs/{job['id']}/save")
                report["saved_image_id"] = saved["id"]
                call(client, "PATCH", f"/images/{saved['id']}/album", json={"album_id": account["albums"]["03 · Entregables DEMO"]})
        report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
