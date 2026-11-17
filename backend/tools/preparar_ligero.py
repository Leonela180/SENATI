"""Cuantiza los pesos existentes sin reemplazar el archivo original."""
import json
import argparse
import shutil
import uuid
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import ROOT
from app.ai.interface import EngineError
from app.ai.processes import run_limited


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=("q4_0", "f16"), default="q4_0")
    parser.add_argument("--source", type=Path, default=ROOT / "models/v1-5-pruned-emaonly.safetensors")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    executable = ROOT / "private_data/tools/stable-diffusion.cpp/sd-cli.exe"
    source = args.source.resolve()
    output = (args.output or ROOT / f"models/sd15-{args.type}.gguf").resolve()
    if output.parent != (ROOT / "models").resolve():
        raise SystemExit("La copia debe quedar dentro de models.")
    log = ROOT / f"private_data/cuantizacion_sd15_{args.type}.log"
    if output.is_file():
        with output.open("rb") as stream:
            if stream.read(4) == b"GGUF" and output.stat().st_size > 1_000_000:
                print("Modelo cuantizado ya preparado.")
                return 0
        raise SystemExit("Existe una conversión incompleta; revisarla antes de continuar.")
    if not executable.is_file() or not source.is_file():
        raise SystemExit("Falta el ejecutable o el modelo local.")
    if shutil.disk_usage(output.parent).free < source.stat().st_size + 512 * 1024**2:
        raise SystemExit("No hay suficiente espacio libre para preparar una copia segura.")
    candidate = output.with_name(output.stem + f".{uuid.uuid4().hex}.building.gguf")
    try:
        result = run_limited([executable, "--mode", "convert", "--model", source,
                              "--type", args.type, "--output", candidate,
                              "--backend", "cpu", "--params-backend", "disk", "--mmap", "--threads", "2"],
                             log, timeout=600, start_free_gib=2.0, cwd=executable.parent)
        with candidate.open("rb") as stream:
            if stream.read(4) != b"GGUF":
                raise EngineError("modelo_no_disponible")
        candidate.rename(output)
        print(json.dumps({"estado": "preparado", "bytes": output.stat().st_size, **result}))
        return 0
    except EngineError as error:
        print("Conversión detenida:", error.code)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
