"""Crea la galería «Ejemplos reales» de la portada aplicando las herramientas REALES del Estudio.

Uso (desde backend/):
    .\\.venv\\Scripts\\python.exe tools\\preparar_ejemplos.py C:\\ruta\\a\\mis_ejemplos
    cd ..\\frontend; npm run build

En la carpeta pon retratos GENERADOS POR IA (propios o autorizados; nunca fotos de personas reales).
El nombre de cada archivo indica la herramienta que se le aplica:
    fondo*.jpg       → Cambiar fondo (color celeste claro)
    desenfoque*.jpg  → Desenfoque del fondo
    calidad*.jpg     → Mejorar calidad (doble resolución + nitidez)
    restaurar*.jpg   → Restaurar foto (ruido y tonos)
    ajustes*.jpg     → Luz y color
    piel*.jpg        → Textura de piel realista
Escribe frontend/public/demo/ej_*.webp y ejemplos.json. No se retoca nada a mano.
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

MAX_SIDE = 1100
EXTS = {".jpg", ".jpeg", ".png", ".webp"}
HERRAMIENTAS = [
    ("fondo", "cambiar_fondo", {"mode": "color", "color": "#e6f0fa"}, "Cambiar fondo",
     "La IA recorta a la persona y reemplaza el fondo por un color limpio, un desenfoque o transparencia."),
    ("desenfoque", "desenfoque", {"scope": "fondo", "radius": 14}, "Desenfoque de fondo",
     "Desenfoque gaussiano solo detrás de la persona, como el modo retrato de una cámara."),
    ("calidad", "mejorar_calidad", {"scale": 2, "sharpen": 0.6, "denoise": True}, "Mejorar calidad",
     "Duplica la resolución, reduce el ruido y recupera nitidez en los bordes."),
    ("restaurar", "restaurar", {"intensity": 0.8, "points": []}, "Restaurar foto",
     "Reduce el ruido y recupera los tonos apagados sin inventar detalles."),
    ("piel", "textura_piel", {"intensity": 0.75, "pecas": False}, "Textura de piel realista",
     "Devuelve poros, grano fino y pequeños brillos a la piel lisa «de plástico» de los retratos de IA."),
    ("ajustes", "ajustes", {"brightness": 1.08, "contrast": 1.06, "saturation": 1.08, "warmth": 0.3, "rotate": 0},
     "Luz y color", "Ajusta brillo, contraste, saturación y calidez con controles simples."),
]


def export_pair(before_path: Path, after_path: Path, out_dir: Path, stem: str) -> tuple[str, str]:
    with Image.open(before_path) as a, Image.open(after_path) as b:
        before = ImageOps.exif_transpose(a).convert("RGB")
        after = b.convert("RGB")
        if before.size != after.size:            # p. ej. «Mejorar calidad»: el antes es la ampliación simple
            before = before.resize(after.size, Image.Resampling.BICUBIC)
        k = min(1.0, MAX_SIDE / max(after.size))
        size = (round(after.width * k), round(after.height * k))
        before.resize(size, Image.Resampling.LANCZOS).save(out_dir / f"ej_{stem}_antes.webp", quality=88, method=6)
        after.resize(size, Image.Resampling.LANCZOS).save(out_dir / f"ej_{stem}_despues.webp", quality=88, method=6)
    return f"/demo/ej_{stem}_antes.webp", f"/demo/ej_{stem}_despues.webp"


def build(folder: Path, out_dir: Path, engine=None) -> list[dict]:
    from app.ai.editing import EditingEngine
    engine = engine or EditingEngine()
    out_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in folder.iterdir() if p.suffix.lower() in EXTS)
    items = []
    for prefix, tool, params, title, text in HERRAMIENTAS:
        for n, src in enumerate(p for p in files if p.stem.lower().startswith(prefix)):
            with tempfile.TemporaryDirectory() as tmp:
                result = Path(tmp) / "resultado.png"
                meta = engine.apply(tool, str(src), str(result), params)
                before, after = export_pair(src, result, out_dir, f"{prefix}{n + 1}")
            items.append({"tool": tool, "title": title, "text": text, "before": before, "after": after,
                          "caption": (f"Retrato generado con IA. Resultado directo de «{title}» en LUMIA "
                                      f"({meta['model_id']}, {meta['seconds']} s en CPU), sin retoques externos.")})
    (out_dir / "ejemplos.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    return items


def main():
    parser = argparse.ArgumentParser(description="Genera los ejemplos reales de la portada.")
    parser.add_argument("carpeta", type=Path)
    args = parser.parse_args()
    if not args.carpeta.is_dir():
        raise SystemExit(f"No existe la carpeta {args.carpeta}")
    from app.config import ROOT
    items = build(args.carpeta, ROOT / "frontend" / "public" / "demo")
    if not items:
        raise SystemExit("No encontré imágenes con nombres fondo*, desenfoque*, calidad*, restaurar*, piel* o ajustes*.")
    for it in items:
        print("✓", it["title"], "→", it["after"])
    print("Ahora compila la web:  cd ..\\frontend; npm run build")


if __name__ == "__main__":
    main()
