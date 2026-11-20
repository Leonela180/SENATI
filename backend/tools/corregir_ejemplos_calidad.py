"""Nuevos trabajos naturales; conserva originales y los resultados anteriores."""
import io
import json
from pathlib import Path
import shutil
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image
from app import create_app
from app.config import ROOT
from preparar_cuentas_demo import call

folder = ROOT / "private_data/demo_senati/calidad_natural_v2"
folder.mkdir(parents=True, exist_ok=True)
report_file = folder / "trabajos.json"
report = json.loads(report_file.read_text(encoding="utf-8")) if report_file.exists() else {}
public = ROOT / "frontend/public/demo"
manifest = public / "ejemplos.json"
if not (folder / "ejemplos_anteriores.json").exists():
    shutil.copyfile(manifest, folder / "ejemplos_anteriores.json")
state = json.loads((ROOT / "private_data/demo_senati/accesos_y_avance.json").read_text(encoding="utf-8"))
account = state["accounts"]["individual1"]
app = create_app(WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False)
client = app.test_client()
call(client, "POST", "/auth/login", json={"email": account["email"], "password": account["password"]})


def persist():
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if not report.get("album_id"):
    name = "05 · Ampliacion natural y etapas DEMO"
    report["album_id"] = next((a["id"] for a in call(client, "GET", "/albums") if a["name"] == name), None) or call(client, "POST", "/albums", json={"name": name})["id"]
    persist()


def process(key, image_id, tool, params):
    entry = report.setdefault(key, {})
    if not entry.get("job_id"):
        job = call(client, "POST", "/jobs", json={"image_id": image_id, "tool": tool, "params": params},
                   headers={"Idempotency-Key": "calidad-natural-v2-"+key})
        entry["job_id"] = job["id"]
        persist()
    start = time.monotonic()
    while True:
        job = call(client, "GET", f"/jobs/{entry['job_id']}")
        if job["status"] in ("completed", "failed"):
            break
        if time.monotonic()-start > 180:
            raise RuntimeError("El trabajo sigue en el historial; no se publica como terminado.")
        time.sleep(1)
    if job["status"] != "completed" or not job["model_version"].endswith("natural-v2") and tool == "mejorar_calidad":
        raise RuntimeError("No se exporta un resultado fallido o de la version anterior.")
    entry.update(status=job["status"], parameters=job["parameters"], model_version=job["model_version"])
    if not entry.get("saved_image_id"):
        saved = call(client, "POST", f"/jobs/{entry['job_id']}/save")
        entry["saved_image_id"] = saved["id"]
        call(client, "PATCH", f"/images/{saved['id']}/album", json={"album_id": report["album_id"]})
    persist()
    print(f"{key}: trabajo {job['id']} completado.", flush=True)
    return entry


quality = process("ampliacion4", account["images"]["0"], "mejorar_calidad", {"scale": 4, "sharpen": .3, "denoise": False})
light = process("etapa_luz", account["images"]["1"], "ajustes", {"brightness": 1.02, "contrast": 1.02, "saturation": 1, "warmth": 0})
stages = process("etapa_ampliacion", light["saved_image_id"], "mejorar_calidad", {"scale": 2, "sharpen": .25, "denoise": False})
items = json.loads(manifest.read_text(encoding="utf-8"))
for key, source, job, stem, title, text in (
    ("mejorar_calidad", account["images"]["0"], quality, "calidad_natural_v2", "Ampliación ×4 · tonos naturales", "Aumenta las dimensiones con enfoque suave; no es 4K ni superresolución generativa."),
    ("flujo_artesana", account["images"]["1"], stages, "etapas_naturales_v2", "Edición natural por etapas", "Luz suave y ampliación ×2, conservando el fondo, los tonos y la textura del retrato.")):
    dimensions = {}
    for stage, url in (("antes", f"/images/{source}/content"), ("despues", f"/jobs/{job['job_id']}/download?inline=1")):
        response = client.get("/api/v1"+url)
        if response.status_code != 200:
            raise RuntimeError("No se pudo obtener la imagen propia.")
        with Image.open(io.BytesIO(response.data)) as image:
            dimensions[stage] = list(image.size)
            image.save(public / f"ej_{stem}_{stage}.webp", "WEBP", quality=96)
    caption = (f"Trabajo real DEMO {job['job_id']}, version natural-v2. Entrada {dimensions['antes'][0]}×{dimensions['antes'][1]} px; salida {dimensions['despues'][0]}×{dimensions['despues'][1]} px. "
               "Original sin reduccion artificial a 256 px. Sin CLAHE ni suavizado intenso. No se reconstruye informacion perdida.")
    replacement = {"tool": key, "title": title, "text": text, "before": f"/demo/ej_{stem}_antes.webp", "after": f"/demo/ej_{stem}_despues.webp",
                   "caption": caption, "metadata": {"job_id": job["job_id"], "model_version": job["model_version"], "parameters": job["parameters"], "dimensions": dimensions}}
    items = [replacement if item.get("tool") == key else item for item in items]
    report[key+"_dimensions"] = dimensions
manifest.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
persist()
print("Ejemplos sustituidos por versiones nuevas; historial y originales anteriores conservados.")
