"""Los ejemplos de la portada salen de las herramientas reales del Estudio."""
import importlib.util
import json
from pathlib import Path

from PIL import Image

SPEC = importlib.util.spec_from_file_location("preparar_ejemplos", Path(__file__).parents[1] / "tools" / "preparar_ejemplos.py")
ejemplos = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ejemplos)


def test_genera_pares_reales_y_json(tmp_path):
    src = tmp_path / "entrada"; src.mkdir()
    Image.new("RGB", (120, 160), (180, 140, 120)).save(src / "calidad_1.png")
    Image.new("RGB", (120, 160), (90, 90, 90)).save(src / "restaurar.png")
    Image.new("RGB", (50, 50)).save(src / "otra_cosa.png")          # sin prefijo conocido: se ignora
    items = ejemplos.build(src, tmp_path / "demo")
    assert [i["tool"] for i in items] == ["mejorar_calidad", "restaurar"]
    assert json.loads((tmp_path / "demo" / "ejemplos.json").read_text(encoding="utf-8")) == items
    with Image.open(tmp_path / "demo" / "ej_calidad1_antes.webp") as a, Image.open(tmp_path / "demo" / "ej_calidad1_despues.webp") as b:
        assert a.size == b.size == (240, 320)                       # el antes es la ampliación simple
    assert all("sin retoques externos" in i["caption"] for i in items)
