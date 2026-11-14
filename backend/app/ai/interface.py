from abc import ABC, abstractmethod
from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngInfo


class EngineError(Exception):
    """Error del motor con un código seguro para el usuario (RF-12)."""
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class HumanizationEngine(ABC):
    model_id: str = ""
    model_version: str = ""

    @abstractmethod
    def humanize(self, input_path: str, output_path: str, preset: str, seed: int | None = None) -> dict:
        """Devuelve metadatos del procesamiento; falla explícitamente ante error."""


def save_labeled(img: Image.Image, output_path: str, source_info: dict, label: str = "editado con IA") -> None:
    """RF-16: rotula el resultado (editado con IA / edición digital) y conserva los metadatos de procedencia del original."""
    meta = PngInfo()
    for key, value in source_info.items():
        if isinstance(value, str) and key not in ("LUMIA-AI", "Software"):
            meta.add_text(key, value)                   # no se borran metadatos de procedencia (skill §9)
    meta.add_text("LUMIA-AI", label)
    meta.add_text("Software", "LUMIA AI")
    kwargs = {"pnginfo": meta}
    if source_info.get("exif"):
        kwargs["exif"] = source_info["exif"]
    img.save(output_path, "PNG", **kwargs)


class MockEngine(HumanizationEngine):
    """SOLO para probar el circuito subida → cola → descarga. Simulación, sin IA real."""
    model_id, model_version = "mock", "simulacion-sin-ia-real"

    def humanize(self, input_path, output_path, preset, seed=None):
        src = Image.open(input_path)
        info = dict(src.info)
        img = src.convert("RGB")
        ImageDraw.Draw(img).text((10, 10), "SIMULACION - SIN IA REAL", fill=(255, 0, 0))
        save_labeled(img, output_path, info)
        return {"model_id": self.model_id, "model_version": self.model_version, "simulated": True, "seconds": 0.0}
