"""Guarda resultados reales terminados y reporta los que continúan en cola."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from app.config import ROOT
from preparar_cuentas_demo import call

folder = ROOT / "private_data/demo_senati"
manifest = folder / "accesos_y_avance.json"
state = json.loads(manifest.read_text(encoding="utf-8"))
pending_file = folder / "humanizaciones.json"
pending = json.loads(pending_file.read_text(encoding="utf-8"))
app = create_app(WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False)
for entry in pending:
    account = state["accounts"][entry["account"]]
    client = app.test_client()
    call(client, "POST", "/auth/login", json={"email": account["email"], "password": account["password"]})
    job = call(client, "GET", f"/jobs/{entry['job_id']}")
    entry.update(status=job["status"], parameters=job["parameters"], error_code=job["error_code"])
    if job["status"] == "completed" and "humanizar-real" not in account["jobs"]:
        if job["model_id"] == "mock":
            raise RuntimeError("No guardar una simulacion como IA real.")
        saved = call(client, "POST", f"/jobs/{job['id']}/save")
        call(client, "PATCH", f"/images/{saved['id']}/album", json={"album_id": account["albums"]["03 · Entregables DEMO"]})
        account["jobs"]["humanizar-real"] = {"id": job["id"], "tool": "humanizar", "saved_image": saved["id"]}
        download = client.get(f"/api/v1/jobs/{job['id']}/download?inline=1")
        assert download.status_code == 200
        (folder / f"humanizacion-{entry['account']}.png").write_bytes(download.data)
manifest.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
pending_file.write_text(json.dumps(pending, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(pending), flush=True)
