"""Publica únicamente ejemplos sintéticos propios desde trabajos DEMO completados."""
import io
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image
from app import create_app
from app.config import ROOT
from preparar_cuentas_demo import call


def main():
    private = ROOT / "private_data/demo_senati"
    state = json.loads((private / "accesos_y_avance.json").read_text(encoding="utf-8"))
    account = state["accounts"]["individual1"]
    app = create_app(WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False)
    client = app.test_client()
    call(client, "POST", "/auth/login", json={"email": account["email"], "password": account["password"]})
    public = ROOT / "frontend/public/demo"
    manifest = public / "ejemplos.json"
    items = json.loads(manifest.read_text(encoding="utf-8"))
    selections = [("1", "1-0", "fondo_artesana", "Fondo de estudio", "Recorte con IA local y fondo de color sobre un retrato sintético propio."),
                  ("1", "1-2", "flujo_artesana", "Edición por etapas", "Fondo, ajustes de luz y ampliación digital x2 encadenados en una cuenta DEMO.")]
    for source, record, key, title, text in selections:
        job_id = account["jobs"][record]["id"]
        job = call(client, "GET", f"/jobs/{job_id}")
        if job["status"] != "completed" or job["model_id"] == "mock":
            raise RuntimeError("Solo se exportan resultados reales completados.")
        before = client.get(f"/api/v1/images/{account['images'][source]}/content")
        after = client.get(f"/api/v1/jobs/{job_id}/download?inline=1")
        if before.status_code != 200 or after.status_code != 200:
            raise RuntimeError("No se pudo descargar el ejemplo propio.")
        for stage, response in (("antes", before), ("despues", after)):
            with Image.open(io.BytesIO(response.data)) as image:
                image.save(public / f"ej_{key}_{stage}.webp", "WEBP", quality=94)
        items = [item for item in items if item.get("tool") != key]
        items.append({"tool": key, "title": title, "text": text,
            "before": f"/demo/ej_{key}_antes.webp", "after": f"/demo/ej_{key}_despues.webp",
            "caption": f"Retrato sintetico propio. Resultado real del trabajo DEMO {job_id}; no es una conversion de dibujo a persona. {text}",
            "metadata": {"job_id": job_id, "tool": job["tool"], "parameters": job["parameters"]}})
    manifest.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    conversion_report = private / "conversion-real-hombre.json"
    if conversion_report.exists():
        report = json.loads(conversion_report.read_text(encoding="utf-8"))
        job = call(client, "GET", f"/jobs/{report['job_id']}")
        if job["status"] == "completed" and job["parameters"].get("filtro_seguridad") is True:
            for stage, url in (("antes", f"/images/{report['image_id']}/content"), ("despues", f"/jobs/{report['job_id']}/download?inline=1")):
                response = client.get("/api/v1" + url)
                if response.status_code != 200:
                    raise RuntimeError("No se pudo exportar la conversion propia.")
                with Image.open(io.BytesIO(response.data)) as image:
                    image.thumbnail((512, 512))
                    image.save(public / f"ej_realista_{stage}.webp", "WEBP", quality=96)
            items = [item for item in items if item.get("tool") != "realista"]
            items.append({"tool": "realista", "title": "Personaje a retrato", "text": "Reinterpretacion local de un personaje adulto sintetico; puede cambiar rasgos, prendas y accesorios.",
                "before": "/demo/ej_realista_antes.webp", "after": "/demo/ej_realista_despues.webp",
                "caption": f"Resultado real DEMO {job['id']}, CPU con offload a disco, {job['parameters']['seconds']} s. Filtros antes/despues aprobados. No representa una identidad real ni garantiza identicos resultados con otros personajes.",
                "metadata": {"job_id": job["id"], "parameters": job["parameters"]}})
            manifest.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Dos ejemplos propios exportados desde sus trabajos reales. Sin credenciales ni fotos privadas.")


if __name__ == "__main__":
    main()
