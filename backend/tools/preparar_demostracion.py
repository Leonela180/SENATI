"""Ejemplos reproducibles del Estudio a partir de un retrato sintetico autorizado.

El deterioro y la reduccion de resolucion de dos entradas son simulados y se
identifican expresamente en cada pie de ejemplo. Los resultados son del editor.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import numpy as np
from PIL import Image, ImageEnhance

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import ROOT
from app.ai.editing import EditingEngine
from preparar_ejemplos import export_pair


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--retrato-sintetico", type=Path, required=True)
    args = parser.parse_args()
    source = args.retrato_sintetico.resolve()
    original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    out = ROOT / "frontend/public/demo"
    out.mkdir(parents=True, exist_ok=True)
    entries = []
    editor = EditingEngine()
    with tempfile.TemporaryDirectory() as directory:
        scratch = Path(directory)
        with Image.open(source) as opened:
            portrait = opened.convert("RGB")
            portrait.thumbnail((800, 1000), Image.Resampling.LANCZOS)
        normal = scratch / "original.png"
        portrait.save(normal)
        small = portrait.copy()
        small.thumbnail((256, 256), Image.Resampling.LANCZOS)
        small.save(scratch / "pequena.png")
        faded = np.asarray(ImageEnhance.Contrast(portrait).enhance(.45), dtype=np.float32)
        faded += np.random.default_rng(1234).normal(0, 3, faded.shape)
        Image.fromarray(faded.clip(0, 255).astype(np.uint8)).save(scratch / "deterioro.png")
        jobs = [
            ("piel", normal, "textura_piel", {"intensity": .65, "pecas": False},
             "Textura de piel", "Microtextura calculada sobre la piel detectada; no cambia la forma del rostro.",
             "Retrato sintetico propio. Edicion digital, no IA generativa."),
            ("calidad", scratch / "pequena.png", "mejorar_calidad", {"scale": 4, "sharpen": .6, "denoise": True},
             "Resolucion x4", "Ampliacion digital con reduccion de ruido, contraste local y enfoque.",
             "Entrada reducida a 256 px para un experimento controlado. El antes se amplia por bicubica para comparar al mismo tamano; no se recupera informacion inexistente."),
            ("restaurar", scratch / "deterioro.png", "restaurar", {"intensity": .65, "points": []},
             "Recuperar tonos", "Correccion conservadora de contraste y ruido sobre una copia.",
             "Deterioro simulado expresamente para demostrar el editor. No es una fotografia antigua real."),
            ("fondo", normal, "cambiar_fondo", {"mode": "color", "color": "#dcebf7", "radius": 12},
             "Fondo de retrato", "Segmentacion local de la persona y sustitucion del fondo por un color.",
             "Retrato sintetico propio. El recorte lo calcula U2-Net en CPU."),
        ]
        for stem, before, tool, params, title, text, disclosure in jobs:
            after = scratch / f"{stem}.png"
            meta = editor.apply(tool, str(before), str(after), params)
            before_url, after_url = export_pair(before, after, out, stem)
            entries.append({"tool": tool, "title": title, "text": text, "before": before_url, "after": after_url,
                            "caption": f"{disclosure} Resultado directo de LUMIA: {meta['seconds']} s.",
                            "metadata": meta})
    (out / "ejemplos.json").write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    skin = entries[0]
    (out / "demo.json").write_text(json.dumps({
        "before": skin["before"], "after": skin["after"],
        "beforeLabel": "Retrato generado con IA", "afterLabel": "Textura digital LUMIA",
        "caption": skin["caption"] + " Esta muestra es del filtro de textura, no de la conversion experimental."
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    report = {"source_sha256": original_hash, "source_synthetic": True,
              "original_preserved": hashlib.sha256(source.read_bytes()).hexdigest() == original_hash,
              "examples": entries}
    evidence = ROOT / "docs/evidencias/etapa_20261119"
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "ejemplos.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Ejemplos reales preparados:", len(entries), "Original conservado:", report["original_preserved"])


if __name__ == "__main__":
    main()
