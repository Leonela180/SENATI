"""Detalle facial convencional tras la IA, inspirado en los prototipos locales.

Detecta cada zona en la imagen actual; no reutiliza coordenadas ni resultados
de un retrato concreto. Conserva los reflejos existentes y protege los rasgos.
"""
import cv2
import numpy as np
from PIL import Image


def detect_regions(image):
    scale = min(1.0, 768 / max(image.size))
    small = image.resize((max(1, round(image.width * scale)), max(1, round(image.height * scale))))
    gray = cv2.cvtColor(np.asarray(small), cv2.COLOR_RGB2GRAY)
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    eyes_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye_tree_eyeglasses.xml")
    if detector.empty() or eyes_detector.empty():
        return None, []
    faces = detector.detectMultiScale(gray, 1.1, 5, minSize=(70, 70))
    if not len(faces):
        return None, []
    x, y, w, h = (int(v) for v in max(faces, key=lambda box: int(box[2]) * int(box[3])))
    candidates = eyes_detector.detectMultiScale(gray[y:y + int(h * .6), x:x + w], 1.1, 5,
                                                minSize=(max(12, w // 10), max(10, h // 12)))
    eyes = []
    for target_x in (.28, .72):
        side = [tuple(int(v) for v in box) for box in candidates
                if .12 * h < box[1] + box[3] / 2 < .57 * h
                and ((box[0] + box[2] / 2 < w / 2) == (target_x < .5))]
        if side:
            ex, ey, ew, eh = min(side, key=lambda box: abs((box[0] + box[2] / 2) / w - target_x))
            eyes.append(tuple(round(v / scale) for v in (x + ex, y + ey, ew, eh)))
    return tuple(round(v / scale) for v in (x, y, w, h)), eyes


def detail_crop(original, generated, eyes, intensity, seed):
    source = np.asarray(original, dtype=np.uint8)
    generated = np.asarray(generated, dtype=np.float32)
    height, width = source.shape[:2]
    gray = cv2.cvtColor(source, cv2.COLOR_RGB2GRAY).astype(np.float32)
    color = cv2.cvtColor(source, cv2.COLOR_RGB2YCrCb).astype(np.float32)
    mask = np.zeros((height, width), np.float32)
    cv2.ellipse(mask, (width // 2, height // 2), (int(width * .45), int(height * .48)), 0, 0, 360, 1, -1)
    samples = []
    for center in (.27, .73):
        x0, x1 = int(width * (center - .04)), int(width * (center + .04))
        y0, y1 = int(height * .54), int(height * .63)
        samples.append(color[y0:y1, x0:x1, 1:].reshape(-1, 2))
    samples = np.concatenate(samples)
    center = np.median(samples, axis=0)
    spread = np.maximum(np.median(np.abs(samples - center), axis=0) * 3, (14, 12))
    distance = np.sum(((color[..., 1:] - center) / spread) ** 2, axis=2)
    mask *= np.clip(1 - distance / 4, 0, 1)
    mask *= (gray > 30)
    # Boca, fosas nasales y contorno ocular no reciben textura.
    cv2.ellipse(mask, (width // 2, int(height * .78)), (int(width * .26), int(height * .11)), 0, 0, 360, 0, -1)
    cv2.ellipse(mask, (width // 2, int(height * .64)), (int(width * .12), int(height * .045)), 0, 0, 360, 0, -1)
    for ex, ey, ew, eh in eyes:
        cv2.rectangle(mask, (max(0, ex - int(ew * .08)), max(0, ey - int(eh * .35))),
                      (min(width - 1, ex + int(ew * 1.08)), min(height - 1, ey + int(eh * 1.12))), 0, -1)
    # Protege lunares y marcas oscuras que ya estaban presentes.
    dark_marks = (gray - cv2.GaussianBlur(gray, (0, 0), 2.0) < -9).astype(np.uint8)
    dark_marks = cv2.dilate(dark_marks, np.ones((3, 3), np.uint8))
    mask[dark_marks > 0] = 0
    soft = cv2.GaussianBlur(mask, (0, 0), max(1.0, width / 200))
    mask = np.minimum(mask, soft)
    rng = np.random.default_rng(seed)
    points = (rng.random((height, width), dtype=np.float32) < .0035).astype(np.float32)
    pores = (cv2.GaussianBlur(points, (0, 0), 2.0) - cv2.GaussianBlur(points, (0, 0), .65)) * 18
    noise = rng.standard_normal((height, width), dtype=np.float32)
    relief = cv2.GaussianBlur(noise, (0, 0), 1.0) - cv2.GaussianBlur(noise, (0, 0), 4.0)
    relief /= max(float(relief.std()), 1e-6)
    generated_gray = cv2.cvtColor(generated, cv2.COLOR_RGB2GRAY)
    existing_detail = gray - cv2.GaussianBlur(gray, (0, 0), 1.2)
    generated_detail = generated_gray - cv2.GaussianBlur(generated_gray, (0, 0), 1.2)
    texture = np.clip(pores + relief * .65, -5, 3) * intensity
    delta = (generated - source) + ((existing_detail - generated_detail) * .85 + texture)[..., None]
    edited = source.astype(np.float32) + delta * mask[..., None]
    eye_count = 0
    for ex, ey, ew, eh in eyes:
        eye_mask = np.zeros_like(mask)
        cv2.ellipse(eye_mask, (int(ex + ew * .5), int(ey + eh * .56)),
                    (max(1, int(ew * .35)), max(1, int(eh * .22))), 0, 0, 360, 1, -1)
        eye_mask = cv2.GaussianBlur(eye_mask, (0, 0), 1)
        highlights = np.clip((gray - cv2.GaussianBlur(gray, (0, 0), 4)) / 25, 0, 1)
        highlights *= (gray > 135) & (source.max(axis=2).astype(np.int16) - source.min(axis=2) < 100)
        eye_delta = np.clip((gray - cv2.GaussianBlur(gray, (0, 0), 1.1)) * .10, -2, 2)
        eye_delta += highlights * (5 * intensity)
        eye_delta *= eye_mask * (gray > 45)
        edited += eye_delta[..., None]
        eye_count += int(np.any(np.abs(eye_delta) >= .5))
    result = np.rint(edited).clip(0, 255).astype(np.uint8)
    return Image.fromarray(result), eye_count, float(np.mean(mask > .1))


def enhance_facial_detail(original, generated, intensity=.65, seed=1234):
    if not 0 <= intensity <= 1 or original.size != generated.size:
        raise ValueError("Intensidad o dimensiones inválidas.")
    metadata = {"facial_detail_applied": False, "eyes_enhanced": 0, "pores_intensity": intensity,
                "facial_detail_method": "OpenCV: microtexture and existing reflections"}
    if intensity == 0:
        return original.copy(), metadata
    face, eyes = detect_regions(original)
    if face is None:
        return generated.copy(), metadata
    x, y, w, h = face
    x, y = max(0, x), max(0, y)
    w, h = min(w, original.width - x), min(h, original.height - y)
    box = (x, y, x + w, y + h)
    source = original.crop(box)
    generated_crop = generated.crop(box)
    scale = min(1.0, 1400 / max(source.size))
    size = (max(1, round(w * scale)), max(1, round(h * scale)))
    source_small = source.resize(size, Image.Resampling.LANCZOS)
    generated_small = generated_crop.resize(size, Image.Resampling.LANCZOS)
    local_eyes = [tuple(round(v * scale) for v in (ex - x, ey - y, ew, eh)) for ex, ey, ew, eh in eyes]
    detail, eye_count, coverage = detail_crop(source_small, generated_small, local_eyes, intensity, seed)
    # Reescala solo la corrección para conservar los píxeles originales y su geometría.
    delta = np.asarray(detail, dtype=np.float32) - np.asarray(source_small, dtype=np.float32)
    if scale < 1:
        delta = cv2.resize(delta, source.size, interpolation=cv2.INTER_LINEAR)
    corrected = np.rint(np.asarray(source, dtype=np.float32) + delta).clip(0, 255).astype(np.uint8)
    result = original.copy()
    result.paste(Image.fromarray(corrected), (x, y))
    metadata.update(facial_detail_applied=coverage > .01, eyes_enhanced=eye_count)
    return result, metadata
