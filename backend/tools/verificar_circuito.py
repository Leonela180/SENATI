"""Ejecuta un trabajo de inferencia REAL de punta a punta con una imagen autorizada (skill §11)."""
import pathlib
import sys
import time
import uuid
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from app import create_app

muestra = pathlib.Path(sys.argv[1])
app = create_app(WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False)
if app.config["AI_ENGINE"] != "local":
    sys.exit("AI_ENGINE no es 'local': esta verificación NO prueba IA real.")
c = app.test_client()
r = c.post("/api/v1/auth/register", json={"email": f"verificacion+{uuid.uuid4().hex[:8]}@lumia.local",
                                           "display_name": "Verificación", "password": "clave-segura-123"})
assert r.status_code == 201, r.json
with muestra.open("rb") as f:
    r = c.post("/api/v1/images", data={"file": (f, muestra.name), "declaracion_ia": "true"}, content_type="multipart/form-data")
assert r.status_code == 201, r.json
r = c.post("/api/v1/jobs", json={"image_id": r.json["data"]["id"], "preset": "natural"}, headers={"Idempotency-Key": uuid.uuid4().hex})
job_id = r.json["data"]["id"]
t0 = time.time()
while time.time() - t0 < 600:
    job = c.get(f"/api/v1/jobs/{job_id}").json["data"]
    if job["status"] in ("completed", "failed"):
        break
    time.sleep(3)
print(f"Trabajo {job_id}: {job['status']} en {round(time.time() - t0, 1)} s · modelo {job['model_id']} {job['model_version']}")
print(f"Parámetros: {job['parameters']}")
assert job["status"] == "completed", f"Falló: {job['error_code']}"
d = c.get(f"/api/v1/jobs/{job_id}/download")
assert d.status_code == 200 and b"editado con IA" in d.data, "El resultado no está rotulado"
print("Inferencia real verificada: OK")
