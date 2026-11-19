"""Estudio de edición de LUMIA AI: herramientas que corren en el procesador (sin GPU NVIDIA).

- quitar_lunar     → relleno inteligente (inpainting de OpenCV) en los puntos que marca el usuario.
- cambiar_fondo    → segmentación de la persona con U²-Net (rembg, ONNX en CPU, ~0,3 s por imagen)
                     y nuevo fondo: color, desenfocado o transparente.
- desenfoque       → desenfoque gaussiano de toda la imagen o solo del fondo (efecto retrato).
- mejorar_calidad  → reducción de ruido, escalado ×2 (Lanczos), contraste local suave (CLAHE) y nitidez.
- ajustes          → brillo, contraste, saturación, calidez y rotación.
- textura_piel     → poros, grano fino y micro-brillos sobre la piel «de plástico» (ver skin_texture.py).

Todas guardan PNG con los metadatos de procedencia y un rótulo de edición (RF-16).
"""
import os
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

from .interface import EngineError, save_labeled

TOOLS = ("quitar_lunar", "cambiar_fondo", "desenfoque", "mejorar_calidad", "ajustes", "restaurar", "textura_piel")
MAX_SIDE_OUT = 4096                      # límite del escalado para no saturar 16 GB de RAM
# u2net (general) recorta bien personas fotográficas y también imágenes generadas o ilustradas; 168 MB, ~0,3 s en CPU.
SEGMENT_MODEL = os.getenv("LUMIA_SEGMENT_MODEL", "u2net")
# Los pesos se guardan en models/rembg del proyecto (fuera de Git); se descargan una sola vez.
os.environ.setdefault("U2NET_HOME", str(Path(__file__).resolve().parents[3] / "models" / "rembg"))
_session = None


def _person_alpha(rgb: np.ndarray) -> np.ndarray:
    """Máscara 0..1 de la persona (1 = persona). Se carga el modelo una sola vez."""
    global _session
    try:
        from rembg import new_session, remove
    except ImportError as e:
        raise EngineError("modelo_no_disponible") from e
    try:
        if _session is None:
            _session = new_session(SEGMENT_MODEL)
        mask = remove(Image.fromarray(rgb), session=_session, only_mask=True)
    except Exception as e:                       # modelo no descargado o dañado
        raise EngineError("modelo_no_disponible") from e
    alpha = np.asarray(mask.convert("L").resize((rgb.shape[1], rgb.shape[0])), dtype=np.float32) / 255.0
    return cv2.GaussianBlur(alpha, (0, 0), 1.2)      # borde suave para que el recorte no se vea duro


def _hex_rgb(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def quitar_lunar(rgb: np.ndarray, points: list[dict]) -> np.ndarray:
    mask = np.zeros(rgb.shape[:2], np.uint8)
    for p in points:
        cv2.circle(mask, (int(p["x"]), int(p["y"])), int(p["r"]), 255, -1)
    if not mask.any():
        raise EngineError("parametros_invalidos")
    radius = max(3, int(max(p["r"] for p in points) * 0.6))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    filled = cv2.cvtColor(cv2.inpaint(bgr, mask, radius, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB)
    # Mezcla con borde suave y un grano muy leve para que la zona no quede "lisa"
    soft = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (0, 0), 2.0)[..., None]
    grain = np.random.default_rng(1234).normal(0, 2.0, rgb.shape).astype(np.float32)
    out = rgb.astype(np.float32) * (1 - soft) + (filled.astype(np.float32) + grain) * soft
    return np.clip(out, 0, 255).astype(np.uint8)


def desenfocar(rgb: np.ndarray, radius: float, scope: str, alpha: np.ndarray | None = None) -> np.ndarray:
    blurred = cv2.GaussianBlur(rgb, (0, 0), max(0.5, radius))
    if scope == "todo":
        return blurred
    a = alpha[..., None]
    return np.clip(rgb * a + blurred * (1 - a), 0, 255).astype(np.uint8)


def cambiar_fondo(rgb: np.ndarray, mode: str, color: str, radius: float, alpha: np.ndarray) -> Image.Image:
    if mode == "transparente":
        rgba = np.dstack([rgb, (alpha * 255).astype(np.uint8)])
        return Image.fromarray(rgba, "RGBA")
    if mode == "desenfocado":
        return Image.fromarray(desenfocar(rgb, radius, "fondo", alpha))
    bg = np.empty_like(rgb)
    bg[:] = _hex_rgb(color)
    a = alpha[..., None]
    return Image.fromarray(np.clip(rgb * a + bg * (1 - a), 0, 255).astype(np.uint8))


def mejorar_calidad(rgb: np.ndarray, scale: int, sharpen: float, denoise: bool) -> np.ndarray:
    img = rgb
    if denoise:
        img = cv2.fastNlMeansDenoisingColored(img, None, 3, 3, 7, 21)
    if scale > 1:
        h, w = img.shape[:2]
        k = min(scale, MAX_SIDE_OUT / max(h, w))
        if k != 1:
            img = cv2.resize(img, (int(w * k), int(h * k)), interpolation=cv2.INTER_LANCZOS4)
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    lab[..., 0] = cv2.createCLAHE(clipLimit=1.4, tileGridSize=(8, 8)).apply(lab[..., 0])
    img = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    if sharpen > 0:                               # máscara de enfoque (unsharp mask)
        soft = cv2.GaussianBlur(img, (0, 0), 1.2)
        img = cv2.addWeighted(img, 1 + sharpen, soft, -sharpen, 0)
    return img


def ajustar(img: Image.Image, brightness: float, contrast: float, saturation: float, warmth: float, rotate: int) -> Image.Image:
    from PIL import ImageEnhance
    out = ImageEnhance.Brightness(img).enhance(brightness)
    out = ImageEnhance.Contrast(out).enhance(contrast)
    out = ImageEnhance.Color(out).enhance(saturation)
    if warmth:                                    # calidez: + rojo/amarillo, − azul
        arr = np.asarray(out, dtype=np.float32)
        arr[..., 0] *= 1 + 0.08 * warmth
        arr[..., 2] *= 1 - 0.08 * warmth
        out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return out.rotate(-rotate, expand=True) if rotate else out


def restaurar(rgb: np.ndarray, strength: float, points: list[dict]) -> np.ndarray:
    """Restauracion conservadora: no genera rostros ni inventa detalles perdidos."""
    # Acota trabajo y memoria incluso con fotografias escaneadas grandes.
    h, w = rgb.shape[:2]
    factor = min(1.0, 1600 / max(h, w))
    work = cv2.resize(rgb, (max(1, round(w * factor)), max(1, round(h * factor)))) if factor < 1 else rgb.copy()
    if points:
        mask = np.zeros(work.shape[:2], np.uint8)
        for point in points:
            cv2.circle(mask, (round(point['x'] * factor), round(point['y'] * factor)),
                       max(1, round(point['r'] * factor)), 255, -1)
        work = cv2.inpaint(work, mask, 3, cv2.INPAINT_TELEA)
    clean = cv2.fastNlMeansDenoisingColored(work, None, 3, 3, 7, 21)
    lab = cv2.cvtColor(clean, cv2.COLOR_RGB2LAB)
    luminance = lab[..., 0]
    lo, hi = np.percentile(luminance, (1, 99))
    if hi - lo > 12:
        lab[..., 0] = np.clip((luminance.astype(np.float32) - lo) * 255 / (hi - lo), 0, 255).astype(np.uint8)
        lab[..., 0] = cv2.createCLAHE(clipLimit=1.3, tileGridSize=(8, 8)).apply(lab[..., 0])
    corrected = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    # Intensidad afecta tono/ruido; las reparaciones elegidas se conservan completas.
    result = cv2.addWeighted(work, 1 - strength, corrected, strength, 0)
    result = cv2.addWeighted(result, 1.2, cv2.GaussianBlur(result, (0, 0), 1), -0.2, 0)
    return cv2.resize(result, (w, h), interpolation=cv2.INTER_LANCZOS4) if factor < 1 else result


class EditingEngine:
    model_id = "lumia-editor"
    model_version = f"opencv-{cv2.__version__}"

    def apply(self, tool: str, input_path: str, output_path: str, params: dict) -> dict:
        if tool not in TOOLS:
            raise EngineError("parametros_invalidos")
        t0 = time.perf_counter()
        src = ImageOps.exif_transpose(Image.open(input_path))
        info = dict(src.info)
        rgb = np.asarray(src.convert("RGB"))
        model_id, label = self.model_id, "editado con LUMIA AI (edición digital)"
        extra = {}
        if tool == "textura_piel":
            from .skin_texture import textura_piel
            arr, extra = textura_piel(rgb, float(params["intensity"]), bool(params.get("pecas", False)))
            out = Image.fromarray(arr)
        elif tool == "restaurar":
            out = Image.fromarray(restaurar(rgb, float(params["intensity"]), params["points"]))
        elif tool == "ajustes":
            out = ajustar(Image.fromarray(rgb), float(params["brightness"]), float(params["contrast"]),
                          float(params["saturation"]), float(params["warmth"]), int(params["rotate"]))
        elif tool == "quitar_lunar":
            out = Image.fromarray(quitar_lunar(rgb, params["points"]))
        elif tool == "mejorar_calidad":
            out = Image.fromarray(mejorar_calidad(rgb, int(params["scale"]), float(params["sharpen"]), bool(params["denoise"])))
        elif tool == "desenfoque" and params["scope"] == "todo":
            out = Image.fromarray(desenfocar(rgb, float(params["radius"]), "todo"))
        else:                                     # usan la segmentación de la persona (modelo de IA)
            alpha = _person_alpha(rgb)
            model_id, label = f"rembg-{SEGMENT_MODEL}", "editado con IA"
            if tool == "desenfoque":
                out = Image.fromarray(desenfocar(rgb, float(params["radius"]), "fondo", alpha))
            else:
                out = cambiar_fondo(rgb, params["mode"], params.get("color", "#ffffff"), float(params.get("radius", 12)), alpha)
        save_labeled(out, output_path, info, label=label)
        return {"model_id": model_id, "model_version": self.model_version, "tool": tool,
                "seconds": round(time.perf_counter() - t0, 2), "width": out.width, "height": out.height, **extra}
