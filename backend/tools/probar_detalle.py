"""Revisa el detalle local sobre una inferencia real existente, sin publicarla."""
import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image, ImageDraw
from app.config import ROOT
from app.ai.facial_detail import detect_regions, enhance_facial_detail


def sheet(images, labels, box, destination):
    crops = [image.crop(box) for image in images]
    scale = min(2, 600 / crops[0].width)
    size = (round(crops[0].width * scale), round(crops[0].height * scale))
    canvas = Image.new("RGB", (size[0] * len(images), size[1] + 30), "#f4efe8")
    for index, crop in enumerate(crops):
        canvas.paste(crop.resize(size), (index * size[0], 30))
        ImageDraw.Draw(canvas).text((index * size[0] + 8, 8), labels[index], fill="black")
    canvas.save(destination)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--intensity", type=float, default=.65)
    args = parser.parse_args()
    original = Image.open(ROOT / "imagenes_prueba/rostro_original.png").convert("RGB")
    base = Image.open(args.base).convert("RGB")
    result, metadata = enhance_facial_detail(original, base, args.intensity)
    destination = ROOT / "private_data/validacion_detalle" / time.strftime("%Y%m%d_%H%M%S")
    destination.mkdir(parents=True, exist_ok=True)
    result.save(destination / "resultado.png")
    face, eyes = detect_regions(original)
    if face:
        x, y, w, h = face
        box = (x + int(w * .12), y + int(h * .45), x + int(w * .4), y + int(h * .7))
        sheet([original, base, result], ["Original", "IA base", "IA + microtextura"], box, destination / "piel.png")
    if eyes:
        x, y, w, h = eyes[0]
        sheet([original, base, result], ["Original", "IA base", "Reflejos existentes"], (x, y, x + w, y + h), destination / "ojos.png")
    (destination / "detalle.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata))
    print("Evidencia privada:", destination)


if __name__ == "__main__":
    main()
