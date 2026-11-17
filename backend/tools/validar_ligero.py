"""Prueba real del motor ligero sin modificar la configuración pública."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image, ImageChops, ImageOps
from app.config import ROOT
from app.ai.interface import EngineError
from app.ai.lite_engine import LiteHumanizationEngine
from app.ai.resources import available_ram_gib


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--side", type=int, default=320)
    parser.add_argument("--blend", type=float, default=0.35)
    parser.add_argument("--model", type=Path, default=ROOT / "models/sd15-q4_0.gguf")
    parser.add_argument("--input", type=Path, default=ROOT / "imagenes_prueba/rostro_original.png")
    args = parser.parse_args()
    source = args.input.resolve()
    directory = ROOT / "private_data/validacion_ligera" / time.strftime("%Y%m%d_%H%M%S")
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / "resultado.png"
    before_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    engine = LiteHumanizationEngine(ROOT / "private_data/tools/stable-diffusion.cpp/sd-cli.exe",
                                    args.model, ROOT / "models/stable-diffusion-v1-5",
                                    ROOT / "private_data/lite_jobs", side=args.side, blend=args.blend)
    engine.diagnostics = directory
    print("Prueba real iniciada: filtro de entrada, inferencia y filtro de salida.", flush=True)
    try:
        metadata = engine.humanize(str(source), str(output), "natural")
        with Image.open(source) as original, Image.open(output) as result:
            original = ImageOps.exif_transpose(original).convert("RGB")
            changed = ImageChops.difference(original, result.convert("RGB")).getbbox() is not None
            valid = (changed and original.size == result.size and result.info.get("LUMIA-AI") == "editado con IA"
                     and hashlib.sha256(source.read_bytes()).hexdigest() == before_hash and metadata["filtro_seguridad"])
        report = {"estado": "validacion_tecnica_superada" if valid else "fallo", "metadata": metadata,
                  "original_intacto": hashlib.sha256(source.read_bytes()).hexdigest() == before_hash}
    except EngineError as error:
        report = {"estado": "bloqueado", "error_code": error.code, "fase": getattr(error, "phase", "inferencia"),
                  "ram_libre_gib": available_ram_gib()}
    (directory / "validacion.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))
    print("Directorio de evidencia:", directory)
    return 0 if report["estado"] == "validacion_tecnica_superada" else 1


if __name__ == "__main__":
    raise SystemExit(main())
