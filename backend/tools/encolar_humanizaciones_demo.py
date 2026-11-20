"""Encola dos humanizaciones reales en cuentas DEMO; el worker las procesa."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from app.config import ROOT
from preparar_cuentas_demo import call

app = create_app(WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False)
if app.config["AI_ENGINE"] != "local":
    raise RuntimeError("No preparar resultados DEMO de humanizacion en simulacion.")
state = json.loads((ROOT / "private_data/demo_senati/accesos_y_avance.json").read_text(encoding="utf-8"))
report = []
for slug, source in (("individual2", "0"), ("individual3", "2")):
    account = state["accounts"][slug]
    client = app.test_client()
    call(client, "POST", "/auth/login", json={"email": account["email"], "password": account["password"]})
    job = call(client, "POST", "/jobs", json={"image_id": account["images"][source], "tool": "humanizar", "preset": "natural"},
               headers={"Idempotency-Key": f"demo-humanizacion-real-{slug}-v1"})
    report.append({"account": slug, "job_id": job["id"], "status": job["status"]})
(ROOT / "private_data/demo_senati/humanizaciones.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report), flush=True)
