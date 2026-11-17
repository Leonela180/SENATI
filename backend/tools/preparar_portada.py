"""Publica en la portada un ejemplo REAL de humanización (antes/después) a partir de un trabajo completado.

Uso (desde backend/, con LUMIA AI configurado):
    .\\.venv\\Scripts\\python.exe tools\\preparar_portada.py --job 12
    cd ..\\frontend; npm run build

Reglas:
- Solo acepta trabajos de «Humanizar» completados con el motor real (nunca la simulación «mock»).
- La imagen debe ser un retrato GENERADO POR IA y propio o autorizado (no fotos de personas reales).
- Escribe frontend/public/demo/antes.webp, despues.webp y demo.json (con su procedencia).
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

MAX_SIDE = 1100


class PortadaError(Exception):
    pass


def export_demo(original_path: Path, result_path: Path, out_dir: Path, caption: str) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(original_path) as a, Image.open(result_path) as b:
        before = ImageOps.exif_transpose(a).convert("RGB")
        after = ImageOps.exif_transpose(b).convert("RGB")
        if after.size != before.size:
            after = after.resize(before.size, Image.Resampling.LANCZOS)
        k = min(1.0, MAX_SIDE / max(before.size))
        size = (round(before.width * k), round(before.height * k))
        before.resize(size, Image.Resampling.LANCZOS).save(out_dir / "antes.webp", quality=88, method=6)
        after.resize(size, Image.Resampling.LANCZOS).save(out_dir / "despues.webp", quality=88, method=6)
    demo = {"before": "/demo/antes.webp", "after": "/demo/despues.webp", "caption": caption}
    (out_dir / "demo.json").write_text(json.dumps(demo, ensure_ascii=False, indent=2), encoding="utf-8")
    return demo


def demo_from_job(job, root: Path, out_dir: Path) -> dict:
    from app.storage.local_private import path_for
    if job.tool != "humanizar":
        raise PortadaError("El trabajo no es una humanización.")
    if job.status != "completed" or not job.result_storage_key:
        raise PortadaError("El trabajo no está completado.")
    if (job.model_id or "").startswith("mock") or job.model_id is None:
        raise PortadaError("Es un resultado de SIMULACIÓN, no de IA real. No se publica en la portada.")
    params = job.parameters or {}
    caption = ("Retrato sintético generado con IA. Izquierda: original. Derecha: el mismo archivo procesado por LUMIA "
               f"({job.model_id}, {params.get('seconds', '?')} s en {params.get('device', 'CPU').upper()}). "
               "No es una fotografía de una persona real.")
    return export_demo(path_for("originals", job.image.original_storage_key),
                       path_for("results", job.result_storage_key), out_dir, caption)


def main():
    parser = argparse.ArgumentParser(description="Publica un antes/después real en la portada.")
    parser.add_argument("--job", type=int, required=True, help="Número del trabajo de Humanizar (aparece en su detalle).")
    args = parser.parse_args()
    from app import create_app
    from app.config import ROOT
    from app.extensions import db
    from app.models import ProcessingJob
    app = create_app()
    with app.app_context():
        job = db.session.get(ProcessingJob, args.job)
        if not job:
            raise SystemExit(f"No existe el trabajo {args.job}.")
        try:
            demo = demo_from_job(job, ROOT, ROOT / "frontend" / "public" / "demo")
        except PortadaError as error:
            raise SystemExit(str(error))
    print("Portada preparada:", json.dumps(demo, ensure_ascii=False))
    print("Ahora compila la web:  cd ..\\frontend; npm run build")


if __name__ == "__main__":
    main()
