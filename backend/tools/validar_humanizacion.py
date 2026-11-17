"""Valida IA local sin cambiar AI_ENGINE ni modificar el original.

Uso: python tools/validar_humanizacion.py --input ../imagenes_prueba/rostro_original.png
Requiere 6 GiB libres al iniciar. Detiene solo su proceso si quedan menos de
1,5 GiB o supera 15 minutos. Un pase técnico requiere después revisión visual.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import Config, ROOT
from app.ai.resources import available_ram_gib


def write_report(path, report):
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def child(source, directory):
    from PIL import Image, ImageChops, ImageOps
    from app.ai.local_engine import LocalHumanizationEngine
    original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    engine = LocalHumanizationEngine(str(Config.AI_MODEL_PATH), Config.AI_MODEL_ID)
    output = directory / "resultado.png"
    metadata = engine.humanize(str(source), str(output), "natural")
    with Image.open(source) as before, Image.open(output) as after:
        original = ImageOps.exif_transpose(before).convert("RGB")
        result = after.convert("RGB")
        valid = (original.size == result.size
                 and ImageChops.difference(original, result).getbbox() is not None
                 and after.info.get("LUMIA-AI") == "editado con IA"
                 and metadata.get("filtro_seguridad") is True
                 and hashlib.sha256(source.read_bytes()).hexdigest() == original_hash)
    write_report(directory / "inferencia.json", {"validacion_tecnica": valid, "metadata": metadata})
    return 0 if valid else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--output", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    source = args.input.resolve()
    if args.worker:
        return child(source, args.output)
    directory = ROOT / "private_data" / "validacion_ia" / time.strftime("%Y%m%d_%H%M%S")
    directory.mkdir(parents=True, exist_ok=True)
    free = available_ram_gib()
    problems = []
    if not source.is_file():
        problems.append("imagen_de_prueba_ausente")
    if not Config.AI_MODEL_PATH.exists():
        problems.append("pesos_ausentes")
    if free is None:
        problems.append("memoria_no_medible")
    elif free < 6.0:
        problems.append("memoria_insuficiente")
    report = {"estado": "bloqueado" if problems else "preparado", "ram_libre_gib": round(free, 2) if free is not None else None,
              "ram_minima_inicio_gib": 6.0, "problemas": problems, "configuracion_modificada": False}
    path = directory / "validacion.json"
    if problems:
        write_report(path, report)
        print(json.dumps(report, ensure_ascii=True))
        return 2
    env = os.environ.copy()
    env.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    with (directory / "proceso.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen([sys.executable, __file__, "--worker", "--input", str(source), "--output", str(directory)],
                                   stdout=log, stderr=subprocess.STDOUT, env=env,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        started = time.monotonic()
        while process.poll() is None:
            available = available_ram_gib()
            if (available is not None and available < 1.5) or time.monotonic() - started > 900:
                report["problemas"].append("limite_de_memoria_o_tiempo")
                if os.name == "nt":
                    subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
                else:
                    process.terminate()
                break
            time.sleep(0.5)
        code = process.wait(timeout=10)
    report["estado"] = "validacion_tecnica_superada_revisar_imagen" if code == 0 and not report["problemas"] else "fallo"
    report["segundos_totales"] = round(time.monotonic() - started, 1)
    write_report(path, report)
    print(json.dumps(report, ensure_ascii=True))
    return 0 if report["estado"].startswith("validacion_tecnica_superada") else 1


if __name__ == "__main__":
    raise SystemExit(main())
