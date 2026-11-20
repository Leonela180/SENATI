"""Sube un original propio y guarda las etapas reales procesadas por el worker."""
import io
import argparse
import json
from pathlib import Path
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image
from app import create_app
from app.config import ROOT
from preparar_cuentas_demo import call

folder = ROOT / "private_data/demo_senati/retrato_nuevo"
record_path = folder / "proceso.json"
record = json.loads(record_path.read_text(encoding="utf-8")) if record_path.exists() else {"demo": True, "steps": {}}
accounts = json.loads((folder.parent / "accesos_y_avance.json").read_text(encoding="utf-8"))
account = accounts["accounts"]["individual4"]
app = create_app(WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False)
if app.config["AI_ENGINE"] != "local":
    raise RuntimeError("Este ejemplo exige humanizacion real, no simulacion.")
client = app.test_client()
call(client, "POST", "/auth/login", json={"email": account["email"], "password": account["password"]})


def persist():
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")


if not record.get("album_id"):
    name = "04 · Retrato nuevo paso a paso DEMO"
    albums = call(client, "GET", "/albums")
    record["album_id"] = next((a["id"] for a in albums if a["name"] == name), None) or call(client, "POST", "/albums", json={"name": name})["id"]
    persist()
if not record.get("image_id"):
    with (folder / "original-generado.png").open("rb") as stream:
        image = call(client, "POST", "/images", data={"file": (stream, "DEMO_retrato_nuevo_original.png"),
                     "permiso_edicion": "true", "album_id": str(record["album_id"])}, content_type="multipart/form-data")
    record["image_id"] = image["id"]
    persist()
image_id = record["image_id"]
public = ROOT / "frontend/public/demo"
parser = argparse.ArgumentParser()
parser.add_argument("--light", action="store_true", help="Textura y luz sin difusion ni segmentacion pesada")
args = parser.parse_args()
record["light_mode"] = args.light
plan = (("textura_piel", {"intensity": .8, "pecas": False}),
        ("ajustes", {"brightness": 1.02, "contrast": 1.06, "saturation": .97, "warmth": .03})) if args.light else (
        ("humanizar", {}), ("textura_piel", {"intensity": .8, "pecas": False}),
        ("cambiar_fondo", {"mode": "color", "color": "#cbded7"}))
for tool, params in plan:
    step = record["steps"].setdefault(tool, {})
    if not step.get("job_id"):
        job = call(client, "POST", "/jobs", json={"image_id": image_id, "tool": tool, "params": params},
                   headers={"Idempotency-Key": "retrato-nuevo-demo-" + tool + "-v1"})
        step["job_id"] = job["id"]
        persist()
    started = time.monotonic()
    while True:
        job = call(client, "GET", f"/jobs/{step['job_id']}")
        if job["status"] in ("completed", "failed"):
            break
        if time.monotonic()-started > 1200:
            raise RuntimeError("El seguimiento agoto su tiempo; el trabajo permanece en el historial.")
        time.sleep(2)
    step.update(status=job["status"], parameters=job["parameters"], error_code=job["error_code"])
    persist()
    if job["status"] != "completed" or job["model_id"] == "mock":
        raise RuntimeError(f"No se publica el resultado {step['job_id']}: {job['status']}")
    if not step.get("saved_image_id"):
        saved = call(client, "POST", f"/jobs/{step['job_id']}/save")
        step["saved_image_id"] = saved["id"]
        persist()
    image_id = step["saved_image_id"]
    response = client.get(f"/api/v1/jobs/{step['job_id']}/download?inline=1")
    if response.status_code != 200:
        raise RuntimeError("No se pudo descargar el resultado propio.")
    (folder / f"{tool}.png").write_bytes(response.data)
    with Image.open(io.BytesIO(response.data)) as image:
        image.thumbnail((1000, 1000))
        image.save(public / f"retrato_nuevo_{tool}.webp", "WEBP", quality=96)
    print(f"Etapa {tool}: trabajo {step['job_id']} completado y guardado.", flush=True)
with Image.open(folder / "original-generado.png") as image:
    image.thumbnail((1000, 1000))
    image.save(public / "retrato_nuevo_antes.webp", "WEBP", quality=96)
record["completed"] = True
persist()
manifest = public / "ejemplos.json"
items = json.loads(manifest.read_text(encoding="utf-8"))
items = [item for item in items if not item.get("tool", "").startswith("retrato_nuevo_")]
for tool, title, text in (("humanizar", "Retrato nuevo · Humanizar", "Humanizacion local del original; el cambio puede ser sutil."),
                          ("textura_piel", "Retrato nuevo · Textura", "Microtextura digital real sobre la piel detectada; ojos y boca protegidos."),
                          ("cambiar_fondo", "Retrato nuevo · Fondo", "Cadena real de humanizacion, textura y cambio de fondo."),
                          ("ajustes", "Retrato nuevo · Textura y luz", "Microtextura seguida de ajustes suaves de luz y contraste. Edicion ligera, sin difusion generativa.")):
    step = record["steps"].get(tool)
    if not step or step.get("status") != "completed":
        continue
    items.append({"tool": "retrato_nuevo_"+tool, "title": title, "text": text,
        "before": "/demo/retrato_nuevo_antes.webp", "after": f"/demo/retrato_nuevo_{tool}.webp",
        "caption": f"Original sintetico propio generado en esta conversacion. Trabajo DEMO {step['job_id']} realmente procesado y guardado en la cuenta individual4. No es un despues generado externamente.",
        "metadata": {"job_id": step["job_id"], "parameters": step["parameters"]}})
manifest.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print("Ejemplo nuevo en PostgreSQL, galeria, historial y archivos publicos propios.", flush=True)
