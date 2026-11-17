"""«Textura de piel realista»: devuelve poros, grano fino y pequeños brillos a la piel lisa «de plástico».

Es una edición digital calculada en el procesador (OpenCV + NumPy), no IA generativa:
- detecta el rostro en la imagen actual (Haar) y usa la misma máscara suave de piel que la humanización,
  que protege ojos, boca, fosas nasales, lunares y el borde del recorte;
- sintetiza la textura a la escala del rostro (un poro mide lo mismo en una foto grande o pequeña);
- solo cambia la luminancia (y un leve moteado de color): no altera el tono, la forma ni los rasgos.
"""
import cv2
import numpy as np
from PIL import Image

from .facial_detail import detect_regions, skin_mask
from .interface import EngineError


def _band(rng, shape, fine, coarse):
    """Ruido pasa-banda normalizado (desviación 1) entre dos escalas, en píxeles."""
    noise = rng.standard_normal(shape, dtype=np.float32)
    band = cv2.GaussianBlur(noise, (0, 0), fine) - cv2.GaussianBlur(noise, (0, 0), coarse)
    return band / max(float(band.std()), 1e-6)


def _spots(rng, shape, density, sigma):
    """Puntos dispersos difuminados, normalizados a un máximo cercano a 1."""
    points = (rng.random(shape, dtype=np.float32) < density).astype(np.float32)
    points *= rng.uniform(.55, 1.0, shape).astype(np.float32)
    spots = cv2.GaussianBlur(points, (0, 0), sigma)
    return spots / max(float(np.percentile(spots[spots > 0], 99)) if np.any(spots > 0) else 1.0, 1e-6)


def wide_skin_mask(crop: np.ndarray, box: tuple, eyes: list) -> np.ndarray:
    """Máscara de piel de TODO el rostro: frente, mandíbula, orejas y cuello, no solo el centro.

    Dentro del recuadro del detector se usa la máscara de la humanización (protege ojos, boca y lunares);
    fuera, la piel se reconoce por su color, muestreado en las mejillas de esta misma imagen.
    """
    height, width = crop.shape[:2]
    bx, by, bw, bh = box
    inner = np.ascontiguousarray(crop[by:by + bh, bx:bx + bw])
    inner_gray = cv2.cvtColor(inner, cv2.COLOR_RGB2GRAY).astype(np.float32)
    placed = np.zeros((height, width), np.float32)
    placed[by:by + bh, bx:bx + bw] = skin_mask(inner, inner_gray, eyes)
    inside = np.zeros((height, width), np.float32)
    inside[by + bh // 8: by + bh - bh // 8, bx + bw // 8: bx + bw - bw // 8] = 1
    inside = cv2.GaussianBlur(inside, (0, 0), bw / 10)
    color = cv2.cvtColor(crop, cv2.COLOR_RGB2YCrCb).astype(np.float32)
    samples = np.concatenate([color[by + int(bh * .54): by + int(bh * .63), bx + int(bw * c0): bx + int(bw * c1)].reshape(-1, 3)
                              for c0, c1 in ((.23, .31), (.69, .77))])
    center = np.median(samples, axis=0)
    spread = np.maximum(np.median(np.abs(samples - center), axis=0) * 3, (40, 8, 7))
    # Color (Cr, Cb) y luz (Y): el cabello claro puede tener el color de la piel, pero no su misma luz y matiz a la vez
    distance = np.sum(((color - center) / spread) ** 2, axis=2)
    skin = cv2.GaussianBlur(np.clip(1 - distance / 4, 0, 1), (0, 0), max(1.5, bw / 80))
    region = np.zeros((height, width), np.float32)
    cv2.ellipse(region, (bx + bw // 2, by + int(bh * .66)), (int(bw * .70), int(bh * .90)), 0, 0, 360, 1, -1)
    region = cv2.GaussianBlur(region, (0, 0), bw / 8)
    mask = inside * placed + (1 - inside) * skin * region
    taper_y = np.clip(np.sin(np.linspace(0, np.pi, height, dtype=np.float32)), 0, 1) ** .4
    taper_x = np.clip(np.sin(np.linspace(0, np.pi, width, dtype=np.float32)), 0, 1) ** .4
    return np.clip(mask * taper_y[:, None] * taper_x[None, :], 0, 1)


def texture_crop(crop: np.ndarray, box: tuple, eyes: list, intensity: float, freckles: bool, seed: int) -> tuple[np.ndarray, float]:
    """Aplica la textura a un recorte amplio del rostro. Devuelve el recorte nuevo y la fracción de piel tratada."""
    height, width = crop.shape[:2]
    mask = wide_skin_mask(crop, box, eyes)
    rng = np.random.default_rng(seed)
    unit = max(.6, box[2] / 520)                                 # tamaño de un poro según el ancho del rostro
    lab = cv2.cvtColor(crop, cv2.COLOR_RGB2LAB).astype(np.float32)
    light = lab[..., 0]
    shading = cv2.GaussianBlur(light, (0, 0), unit * 10)
    # Poros: hoyitos oscuros con un borde apenas más claro (así se ven en una foto real)
    pores = _spots(rng, (height, width), .0055, unit * .9)
    rims = _spots(rng, (height, width), .0055, unit * 1.8)
    pores_relief = -pores * 11 + (rims - pores) * 2.5
    grain = _band(rng, (height, width), unit * .55, unit * 2.4) * 3.2      # grano fino de la piel
    mottle = _band(rng, (height, width), unit * 6, unit * 22)                # irregularidad suave (no uniforme)
    # Micro-brillos: solo donde la luz ya pega (pómulos, nariz, frente), nunca en las sombras
    reference = float(np.percentile(shading[mask > .3], 60)) if np.any(mask > .3) else 255.0
    lit = np.clip((shading - reference) / 18, 0, 1)
    sparkle = _spots(rng, (height, width), .004, unit * .7) * lit * 9
    # La textura es proporcional a la luz local: en las sombras se nota menos (como en la realidad)
    tone = np.clip(shading / 170, .45, 1.15)
    delta_l = (pores_relief + grain + mottle * 2.0) * tone + sparkle
    delta_a = mottle * 1.3                                                 # leve variación rojiza
    delta_b = np.zeros_like(delta_a)
    if freckles:                                                           # pecas suaves en mejillas y nariz
        zone = np.zeros((height, width), np.float32)
        bx, by, bw, bh = box
        cv2.ellipse(zone, (bx + bw // 2, by + int(bh * .52)), (int(bw * .34), int(bh * .13)), 0, 0, 360, 1, -1)
        zone = cv2.GaussianBlur(zone, (0, 0), bw / 14)
        dots = _spots(rng, (height, width), .0009, unit * 1.6) * zone
        delta_l -= dots * 14
        delta_b += dots * 6
        delta_a += dots * 2.5
    weight = np.clip((mask - .08) / .92, 0, 1) * intensity          # sin «velo» de textura fuera de la piel
    lab[..., 0] += delta_l * weight
    lab[..., 1] += delta_a * weight
    lab[..., 2] += delta_b * weight
    out = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)
    # Fuera de la máscara el píxel queda EXACTAMENTE igual que el original
    out[weight < 1e-3] = crop[weight < 1e-3]
    return out, float(np.mean(mask > .1))


def textura_piel(rgb: np.ndarray, intensity: float, freckles: bool = False, seed: int = 1234) -> tuple[np.ndarray, dict]:
    if not 0 < intensity <= 1:
        raise EngineError("parametros_invalidos")
    face, eyes = detect_regions(Image.fromarray(rgb))
    if face is None:
        raise EngineError("sin_rostro")
    fx, fy, fw, fh = face
    # Recorte amplio: frente completa arriba, mandíbula y cuello abajo
    x0, y0 = max(0, fx - int(fw * .45)), max(0, fy - int(fh * .45))
    x1, y1 = min(rgb.shape[1], fx + fw + int(fw * .45)), min(rgb.shape[0], fy + fh + int(fh * .85))
    fw, fh = min(fw, rgb.shape[1] - fx), min(fh, rgb.shape[0] - fy)
    crop = np.ascontiguousarray(rgb[y0:y1, x0:x1])
    box = (fx - x0, fy - y0, fw, fh)
    local_eyes = [(ex - fx, ey - fy, ew, eh) for ex, ey, ew, eh in eyes]
    textured, coverage = texture_crop(crop, box, local_eyes, intensity, freckles, seed)
    out = rgb.copy()
    out[y0:y1, x0:x1] = textured
    return out, {"rostro_detectado": True, "ojos_protegidos": len(eyes), "cobertura_piel": round(coverage, 3)}
