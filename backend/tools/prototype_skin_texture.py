import argparse
import json
import math
import time
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "imagenes_prueba" / "rostro_original.png"
DEFAULT_OUTPUT_ROOT = ROOT / "private_data" / "results" / "skin_texture"
EXPECTED_SIZE = (1254, 1254)
RELIEF_INTENSITIES = (0.25, 0.50, 0.75)
RELIEF_REGION_SPECS = {
    "frente": {"scales": (3, 7, 18), "weights": (0.58, 0.30, 0.12), "gain": 3.1},
    "mejilla_izquierda": {
        "scales": (4, 9, 22),
        "weights": (0.50, 0.34, 0.16),
        "gain": 3.3,
    },
    "mejilla_derecha": {
        "scales": (4, 9, 22),
        "weights": (0.50, 0.34, 0.16),
        "gain": 3.3,
    },
    "rostro_completo": {
        "scales": (3, 7, 18),
        "weights": (0.54, 0.32, 0.14),
        "gain": 3.2,
    },
}
MASK_SCOPES = ("classic", "full-face")
VARIANT_SPECS = (
    {
        "name": "sutil",
        "pores": 0.45,
        "pore_density": 1.25,
        "freckles": 18,
        "color_variation": 0.15,
        "freckle_opacity": (0.020, 0.045),
        "freckle_color_jitter": 2.0,
    },
    {
        "name": "media",
        "pores": 0.65,
        "pore_density": 1.75,
        "freckles": 30,
        "color_variation": 0.22,
        "freckle_opacity": (0.025, 0.050),
        "freckle_color_jitter": 3.0,
    },
    {
        "name": "visible",
        "pores": 0.85,
        "pore_density": 2.35,
        "freckles": 42,
        "color_variation": 0.30,
        "freckle_opacity": (0.030, 0.055),
        "freckle_color_jitter": 4.0,
    },
)
CROP_REGIONS = (
    ("frente", (400, 100, 860, 270)),
    ("mejilla_izquierda", (350, 470, 510, 710)),
    ("mejilla_derecha", (744, 470, 904, 710)),
)

SKIN_POLYGONS = (
    (
        (423, 142),
        (452, 127),
        (490, 119),
        (525, 122),
        (560, 127),
        (600, 129),
        (650, 128),
        (700, 124),
        (750, 128),
        (792, 137),
        (827, 155),
        (841, 190),
        (837, 225),
        (815, 247),
        (780, 251),
        (744, 246),
        (706, 248),
        (670, 252),
        (620, 248),
        (580, 254),
        (540, 250),
        (500, 253),
        (465, 248),
        (438, 234),
        (421, 208),
    ),
    (
        (391, 520),
        (410, 500),
        (445, 497),
        (476, 520),
        (489, 560),
        (481, 600),
        (465, 645),
        (449, 680),
        (425, 694),
        (400, 689),
        (382, 670),
        (372, 638),
        (376, 598),
        (378, 560),
    ),
    (
        (863, 520),
        (844, 500),
        (809, 497),
        (778, 520),
        (765, 560),
        (773, 600),
        (789, 645),
        (805, 680),
        (829, 694),
        (854, 689),
        (872, 670),
        (882, 638),
        (878, 598),
        (876, 560),
    ),
)
FULL_FACE_SKIN_POLYGON = (
    (627, 73),
    (590, 77),
    (552, 86),
    (516, 100),
    (482, 119),
    (451, 143),
    (424, 171),
    (401, 204),
    (382, 240),
    (365, 285),
    (350, 327),
    (335, 370),
    (324, 414),
    (316, 460),
    (312, 507),
    (313, 554),
    (319, 600),
    (329, 645),
    (344, 690),
    (362, 734),
    (385, 777),
    (411, 820),
    (442, 860),
    (477, 896),
    (516, 928),
    (557, 957),
    (596, 982),
    (627, 1002),
    (658, 982),
    (697, 957),
    (738, 928),
    (777, 896),
    (812, 860),
    (843, 820),
    (869, 777),
    (892, 734),
    (910, 690),
    (925, 645),
    (935, 600),
    (941, 554),
    (942, 507),
    (938, 460),
    (930, 414),
    (919, 370),
    (904, 327),
    (889, 285),
    (872, 240),
    (853, 204),
    (830, 171),
    (803, 143),
    (772, 119),
    (738, 100),
    (702, 86),
    (664, 77),
)
LEFT_EYE_BROW_PROTECTION = (
    (369, 333),
    (378, 315),
    (398, 303),
    (419, 297),
    (440, 295),
    (463, 298),
    (485, 304),
    (507, 310),
    (528, 320),
    (548, 331),
    (565, 345),
    (578, 359),
    (585, 375),
    (586, 393),
    (582, 411),
    (575, 428),
    (563, 444),
    (547, 457),
    (528, 466),
    (507, 472),
    (485, 475),
    (462, 472),
    (440, 466),
    (420, 457),
    (402, 445),
    (387, 430),
    (376, 412),
    (369, 392),
    (367, 369),
)
NOSTRIL_PROTECTION = (
    (
        (578, 654),
        (580, 647),
        (586, 642),
        (594, 640),
        (602, 642),
        (608, 647),
        (611, 653),
        (608, 659),
        (602, 663),
        (594, 664),
        (586, 662),
        (580, 659),
    ),
    (
        (643, 653),
        (646, 647),
        (652, 642),
        (660, 640),
        (668, 642),
        (674, 647),
        (676, 654),
        (674, 659),
        (668, 662),
        (660, 664),
        (652, 663),
        (646, 659),
    ),
)
LIP_PROTECTION = (
    (489, 780),
    (510, 757),
    (546, 744),
    (585, 744),
    (627, 752),
    (669, 744),
    (708, 744),
    (744, 757),
    (770, 778),
    (793, 802),
    (789, 831),
    (773, 854),
    (746, 873),
    (709, 888),
    (668, 895),
    (627, 897),
    (586, 895),
    (545, 888),
    (508, 873),
    (481, 854),
    (465, 831),
    (461, 802),
)
NECK_TRANSITION_PROPOSAL = (
    (557, 957),
    (596, 982),
    (627, 1002),
    (658, 982),
    (697, 957),
    (711, 986),
    (680, 1014),
    (640, 1033),
    (627, 1037),
    (614, 1033),
    (574, 1014),
    (543, 986),
)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Reversible, conventional skin microtexture prototype. By default, "
            "creates a mask preview and does not process the photo."
        )
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    run_mode = parser.add_mutually_exclusive_group()
    run_mode.add_argument(
        "--run",
        action="store_true",
        help="Process one variant after reviewing a mask PNG and passing it with --mask.",
    )
    run_mode.add_argument(
        "--run-variants",
        action="store_true",
        help="Create the approved subtle, medium, and visible comparison set.",
    )
    run_mode.add_argument(
        "--run-relief",
        action="store_true",
        help="Create continuous multiscale microrelief variants without pores or freckles.",
    )
    run_mode.add_argument(
        "--prepare-full-face-mask",
        action="store_true",
        help="Create a full-face skin-mask preview without processing the image.",
    )
    parser.add_argument(
        "--mask-scope",
        choices=MASK_SCOPES,
        default="classic",
        help="Editable area for --run-relief; classic remains the default.",
    )
    parser.add_argument(
        "--relief-intensities",
        nargs="+",
        type=float,
        default=list(RELIEF_INTENSITIES),
        help="Intensity values from 0 to 1 for --run-relief.",
    )
    parser.add_argument("--mask", type=Path, help="Reviewed grayscale mask: white edits, black protects.")
    parser.add_argument("--pores", type=float, default=0.35, help="Pore texture intensity, 0..1.")
    parser.add_argument("--pore-density", type=float, default=1.0, help="Pore count multiplier, 0..5.")
    parser.add_argument("--freckles", type=int, default=20, help="Number of subtle freckle marks, 0..300.")
    parser.add_argument("--freckle-color-jitter", type=float, default=2.0)
    parser.add_argument(
        "--color-variation",
        type=float,
        default=0.20,
        help="Low-frequency local tone variation, 0..1.",
    )
    parser.add_argument("--freckle-opacity-min", type=float, default=0.025)
    parser.add_argument("--freckle-opacity-max", type=float, default=0.050)
    parser.add_argument("--seed", type=int, default=1234)
    return parser.parse_args()


def load_original(path):
    path = path.expanduser().resolve(strict=True)
    with Image.open(path) as probe:
        image_format = probe.format
        probe.verify()
    if image_format != "PNG":
        raise ValueError("This prototype accepts the original PNG only.")
    with Image.open(path) as source:
        image = source.convert("RGB")
    if image.size != EXPECTED_SIZE:
        raise ValueError(f"Expected {EXPECTED_SIZE[0]}x{EXPECTED_SIZE[1]}, got {image.size}.")
    return path, image


def build_safe_mask(size):
    if size != EXPECTED_SIZE:
        raise ValueError(f"Mask polygons are calibrated only for {EXPECTED_SIZE}.")
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    for polygon in SKIN_POLYGONS:
        draw.polygon(polygon, fill=255)
    draw.ellipse((423, 612, 449, 638), fill=0)
    return np.asarray(mask, dtype=np.uint8).copy()


def build_full_face_mask(size):
    if size != EXPECTED_SIZE:
        raise ValueError(f"Full-face mask landmarks are calibrated only for {EXPECTED_SIZE}.")
    face = Image.new("L", size, 0)
    ImageDraw.Draw(face).polygon(FULL_FACE_SKIN_POLYGON, fill=255)

    protected = Image.new("L", size, 0)
    draw = ImageDraw.Draw(protected)
    draw.polygon(LEFT_EYE_BROW_PROTECTION, fill=255)
    right_eye_brow = tuple((size[0] - 1 - x, y) for x, y in LEFT_EYE_BROW_PROTECTION)
    draw.polygon(right_eye_brow, fill=255)
    draw.polygon(LIP_PROTECTION, fill=255)
    for polygon in NOSTRIL_PROTECTION:
        draw.polygon(polygon, fill=255)
    draw.ellipse((428, 613, 444, 629), fill=255)
    draw.ellipse((373, 720, 385, 734), fill=255)
    draw.ellipse((891, 701, 907, 717), fill=255)

    face_array = np.asarray(face, dtype=np.uint8).copy()
    protected_array = np.asarray(protected, dtype=np.uint8).copy()
    editable_array = face_array.copy()
    editable_array[protected_array > 0] = 0
    outer_feather = np.asarray(
        face.filter(ImageFilter.GaussianBlur(radius=10.0)), dtype=np.uint8
    )
    feature_feather = np.asarray(
        protected.filter(ImageFilter.GaussianBlur(radius=2.5)), dtype=np.uint8
    )
    feathered = np.minimum(outer_feather, 255 - feature_feather)
    feathered = np.minimum(feathered, face_array)
    feathered[protected_array > 0] = 0
    neck_proposal = Image.new("L", size, 0)
    ImageDraw.Draw(neck_proposal).polygon(NECK_TRANSITION_PROPOSAL, fill=255)
    return (
        editable_array,
        feathered,
        protected_array,
        np.asarray(neck_proposal, dtype=np.uint8).copy(),
    )


def create_full_face_mask_preview(image, mask, editable, protected, neck_proposal, path):
    source = np.asarray(image, dtype=np.float32)
    face = Image.new("L", image.size, 0)
    ImageDraw.Draw(face).polygon(FULL_FACE_SKIN_POLYGON, fill=255)
    face_array = np.asarray(face, dtype=np.uint8) > 0
    feature_protection = (protected > 0) & face_array
    full_edit = mask == 255
    transition = (mask > 0) & (mask < 255)
    layers = (
        (full_edit, (35, 220, 80), 0.40),
        (transition, (255, 190, 25), 0.58),
        (feature_protection, (240, 55, 55), 0.52),
        (neck_proposal > 0, (90, 150, 255), 0.48),
    )
    preview = source.copy()
    for area, color, strength in layers:
        alpha = (area.astype(np.float32) * strength)[..., None]
        tint = np.asarray(color, dtype=np.float32)
        preview = preview * (1.0 - alpha) + tint * alpha

    image_preview = Image.fromarray(np.rint(preview).clip(0, 255).astype(np.uint8))
    draw = ImageDraw.Draw(image_preview)
    draw.line(
        (*FULL_FACE_SKIN_POLYGON, FULL_FACE_SKIN_POLYGON[0]),
        fill=(255, 255, 255),
        width=2,
        joint="curve",
    )

    header_height = 72
    canvas = Image.new("RGB", (image.width, image.height + header_height), (24, 27, 31))
    canvas.paste(image_preview, (0, header_height))
    legend = ImageDraw.Draw(canvas)
    legend_items = (
        ((35, 220, 80), "PIEL EDITABLE"),
        ((255, 190, 25), "TRANSICION SUAVE"),
        ((240, 55, 55), "RASGOS PROTEGIDOS"),
        ((90, 150, 255), "CUELLO OPCIONAL - NO INCLUIDO"),
    )
    x = 14
    for color, label in legend_items:
        legend.rectangle((x, 21, x + 20, 41), fill=color)
        legend.text((x + 27, 24), label, fill=(245, 245, 245))
        x += 31 + len(label) * 7
    canvas.save(path, format="PNG")


def prepare_full_face_mask(image, input_path, output_root):
    editable, feathered, protected, neck_proposal = build_full_face_mask(image.size)
    review_dir = unique_directory(output_root, "full_face_mask_review")
    Image.fromarray(feathered, mode="L").save(review_dir / "full_face_skin_mask.png")
    Image.fromarray(editable, mode="L").save(
        review_dir / "full_face_skin_mask_binary.png"
    )
    Image.fromarray(neck_proposal, mode="L").save(
        review_dir / "neck_transition_proposal_not_included.png"
    )
    create_full_face_mask_preview(
        image,
        feathered,
        editable,
        protected,
        neck_proposal,
        review_dir / "full_face_mask_preview.png",
    )
    face = Image.new("L", image.size, 0)
    ImageDraw.Draw(face).polygon(FULL_FACE_SKIN_POLYGON, fill=255)
    protected_in_face = (protected > 0) & (np.asarray(face, dtype=np.uint8) > 0)
    details = {
        "input": input_path.name,
        "input_size": list(image.size),
        "mask_convention": "white in the grayscale mask = editable; black = protected",
        "editable_pixel_count": int(np.count_nonzero(feathered)),
        "fully_editable_pixel_count": int(np.count_nonzero(feathered == 255)),
        "transition_pixel_count": int(np.count_nonzero((feathered > 0) & (feathered < 255))),
        "protected_feature_pixel_count": int(np.count_nonzero(protected_in_face)),
        "continuous_face_area": [
            "forehead",
            "temples",
            "cheeks",
            "nose and sides of nose",
            "philtrum",
            "chin",
            "jaw",
        ],
        "protected_areas": [
            "eyes, eyelashes, eyebrows",
            "nostril openings",
            "lips",
            "hair and face perimeter",
            "background, ears, clothing and neck",
            "three visible existing marks",
        ],
        "face_edge_feather_radius_px": 10.0,
        "feature_protection_feather_radius_px": 2.5,
        "neck_transition": {
            "file": "neck_transition_proposal_not_included.png",
            "included_in_edit_mask": False,
            "note": "Illustrative proposal only; requires separate approval before any neck processing.",
        },
        "review_note": "Preview only; no texture was applied. Review and edit the mask before authorizing processing.",
    }
    (review_dir / "mask_review.json").write_text(
        json.dumps(details, indent=2), encoding="utf-8"
    )
    print(f"MASK_PREVIEW={review_dir / 'full_face_mask_preview.png'}")
    print(f"MASK={review_dir / 'full_face_skin_mask.png'}")
    print(f"BINARY_MASK={review_dir / 'full_face_skin_mask_binary.png'}")
    print(f"NECK_PROPOSAL={review_dir / 'neck_transition_proposal_not_included.png'}")
    print(f"SUMMARY={review_dir / 'mask_review.json'}")
    print("No texture was applied. Review the full-face mask before processing.")
    return review_dir


def create_mask_preview(image, mask, path):
    source = np.asarray(image, dtype=np.float32)
    alpha = (mask.astype(np.float32) / 255.0 * 0.42)[..., None]
    tint = np.zeros_like(source)
    tint[..., 1] = 255
    preview = np.rint(source * (1.0 - alpha) + tint * alpha).clip(0, 255).astype(np.uint8)
    preview_image = Image.fromarray(preview)
    draw = ImageDraw.Draw(preview_image)
    for polygon in SKIN_POLYGONS:
        draw.line((*polygon, polygon[0]), fill=(255, 255, 255), width=2, joint="curve")
    draw.ellipse((423, 612, 449, 638), outline=(255, 255, 255), width=2)
    preview_image.save(path, format="PNG")


def unique_directory(root, prefix):
    root.mkdir(parents=True, exist_ok=True)
    base = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    candidate = root / base
    suffix = 1
    while candidate.exists():
        candidate = root / f"{base}_{suffix}"
        suffix += 1
    candidate.mkdir()
    return candidate


def prepare_mask(image, output_root):
    review_dir = unique_directory(output_root, "mask_review")
    safe_mask = build_safe_mask(image.size)
    Image.fromarray(safe_mask, mode="L").save(review_dir / "skin_mask.png")
    create_mask_preview(image, safe_mask, review_dir / "mask_review.png")
    details = {
        "input_size": list(image.size),
        "editable_pixel_count": int(np.count_nonzero(safe_mask)),
        "mask_convention": "white=editable skin; black=protected",
        "editable_regions": ["forehead", "left cheek", "right cheek"],
        "excluded_existing_mark": "small existing spot on left cheek",
        "note": "Review and optionally paint this mask before running with --run --mask.",
    }
    (review_dir / "mask_review.json").write_text(
        json.dumps(details, indent=2), encoding="utf-8"
    )
    print(f"MASK={review_dir / 'skin_mask.png'}")
    print(f"PREVIEW={review_dir / 'mask_review.png'}")
    print("No texture was applied. Review/edit the mask before processing.")
    return review_dir


def normalize_noise(noise):
    noise = noise.astype(np.float32, copy=False)
    noise = noise - float(noise.mean())
    std = float(noise.std())
    if std < 1e-6:
        return np.zeros_like(noise)
    return noise / std


def smooth_noise(rng, width, height, grid_spacing):
    grid_width = max(2, math.ceil(width / grid_spacing))
    grid_height = max(2, math.ceil(height / grid_spacing))
    small = rng.standard_normal((grid_height, grid_width), dtype=np.float32)
    resized = Image.fromarray(small).resize((width, height), Image.Resampling.BICUBIC)
    return normalize_noise(np.asarray(resized, dtype=np.float32))


def sample_points(allowed, count, minimum_distance, rng):
    candidates = np.argwhere(allowed)
    if count <= 0 or candidates.size == 0:
        return []
    chosen = []
    min_distance_sq = minimum_distance * minimum_distance
    max_attempts = max(100, count * 80)
    for _ in range(max_attempts):
        y, x = candidates[int(rng.integers(0, len(candidates)))]
        if all((int(x) - px) ** 2 + (int(y) - py) ** 2 >= min_distance_sq for px, py in chosen):
            chosen.append((int(x), int(y)))
            if len(chosen) == count:
                break
    return chosen


def sample_clustered_points(allowed, count, rng):
    candidates = np.argwhere(allowed)
    if count <= 0 or candidates.size == 0:
        return []
    cluster_count = min(4, count)
    centers = sample_points(allowed, cluster_count, 30.0, rng)
    if not centers:
        return sample_points(allowed, count, 7.5, rng)

    points = []
    max_attempts = max(100, count * 100)
    for _ in range(max_attempts):
        if rng.random() < 0.72:
            center_x, center_y = centers[int(rng.integers(0, len(centers)))]
            x = int(round(rng.normal(center_x, 20.0)))
            y = int(round(rng.normal(center_y, 20.0)))
            if not (0 <= y < allowed.shape[0] and 0 <= x < allowed.shape[1]):
                continue
            if not allowed[y, x]:
                continue
        else:
            y, x = candidates[int(rng.integers(0, len(candidates)))]
            x, y = int(x), int(y)
        if all((x - px) ** 2 + (y - py) ** 2 >= 7.5**2 for px, py in points):
            points.append((x, y))
            if len(points) == count:
                break
    return points


def add_pore_marks(delta, allowed, intensity, density_multiplier, rng):
    height, width = allowed.shape
    area = int(np.count_nonzero(allowed))
    count = min(1800, int(area * 0.010 * 0.35 * density_multiplier))
    points = sample_points(allowed, count, 3.2, rng)
    for x, y in points:
        radius_x = float(rng.uniform(0.55, 1.15))
        radius_y = radius_x * float(rng.uniform(0.75, 1.25))
        angle = float(rng.uniform(0.0, math.tau))
        strength = float(rng.uniform(1.0, 2.1)) * intensity
        x0, x1 = max(0, x - 4), min(width, x + 5)
        y0, y1 = max(0, y - 4), min(height, y + 5)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        dx, dy = xx - x, yy - y
        rotated_x = dx * math.cos(angle) + dy * math.sin(angle)
        rotated_y = -dx * math.sin(angle) + dy * math.cos(angle)
        core = np.exp(-0.5 * ((rotated_x / radius_x) ** 2 + (rotated_y / radius_y) ** 2))
        highlight = np.exp(
            -0.5
            * (
                ((rotated_x + 0.6) / (radius_x + 0.55)) ** 2
                + ((rotated_y + 0.35) / (radius_y + 0.55)) ** 2
            )
        )
        delta[y0:y1, x0:x1] += -strength * core + strength * 0.06 * highlight
    return len(points)


def add_freckles(rgb, allowed, count, opacity_range, color_jitter, rng):
    height, width = allowed.shape
    points = sample_clustered_points(allowed, count, rng)
    for x, y in points:
        radius_x = float(rng.uniform(0.8, 2.1))
        radius_y = float(rng.uniform(0.7, 1.6))
        angle = float(rng.uniform(0.0, math.tau))
        opacity = float(rng.uniform(*opacity_range))
        color_shift = rng.uniform(-color_jitter, color_jitter, size=3).astype(np.float32)
        color_shift -= float(color_shift.mean())
        x0, x1 = max(0, x - 4), min(width, x + 5)
        y0, y1 = max(0, y - 4), min(height, y + 5)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        dx, dy = xx - x, yy - y
        rotated_x = dx * math.cos(angle) + dy * math.sin(angle)
        rotated_y = -dx * math.sin(angle) + dy * math.cos(angle)
        profile = np.exp(
            -0.5 * ((rotated_x / radius_x) ** 2 + (rotated_y / radius_y) ** 2)
        )
        rgb[y0:y1, x0:x1] *= 1.0 - opacity * profile[..., None]
        rgb[y0:y1, x0:x1] += profile[..., None] * color_shift
    return len(points)


def process_image(
    source_image,
    mask,
    pores,
    freckles,
    color_variation,
    seed,
    pore_density=1.0,
    freckle_opacity=(0.025, 0.050),
    freckle_color_jitter=0.0,
):
    source = np.asarray(source_image, dtype=np.uint8)
    height, width = mask.shape
    if source.shape[:2] != (height, width):
        raise ValueError("Image and mask dimensions do not match.")
    if not 0.0 <= pores <= 1.0:
        raise ValueError("--pores must be between 0 and 1.")
    if not 0.0 <= pore_density <= 5.0:
        raise ValueError("--pore-density must be between 0 and 5.")
    if not 0 <= freckles <= 300:
        raise ValueError("--freckles must be between 0 and 300.")
    if not 0.0 <= color_variation <= 1.0:
        raise ValueError("--color-variation must be between 0 and 1.")
    if not 0.0 <= freckle_color_jitter <= 10.0:
        raise ValueError("--freckle-color-jitter must be between 0 and 10.")
    if not 0.0 <= freckle_opacity[0] <= freckle_opacity[1] <= 0.2:
        raise ValueError("Freckle opacity must satisfy 0 <= minimum <= maximum <= 0.2.")
    if seed < 0:
        raise ValueError("--seed must be non-negative.")
    if (
        pores == 0.0
        and freckles == 0
        and color_variation == 0.0
    ):
        return source.copy(), 0, 0

    pore_seed, freckle_seed, tone_seed = np.random.SeedSequence(seed).spawn(3)
    pore_rng = np.random.default_rng(pore_seed)
    freckle_rng = np.random.default_rng(freckle_seed)
    tone_rng = np.random.default_rng(tone_seed)
    editable = mask > 0
    eroded_image = Image.fromarray(editable.astype(np.uint8) * 255).filter(
        ImageFilter.MinFilter(9)
    )
    point_region = np.asarray(eroded_image) > 0
    delta = np.zeros((height, width), dtype=np.float32)

    if pores > 0.0:
        medium = smooth_noise(pore_rng, width, height, 7)
        coarse = smooth_noise(pore_rng, width, height, 23)
        fine = pore_rng.standard_normal((height, width), dtype=np.float32)
        fine_smoothing = smooth_noise(pore_rng, width, height, 3)
        high_frequency = normalize_noise(fine - fine_smoothing)
        delta += pores * (0.85 * medium + 0.45 * coarse + 0.12 * high_frequency)
        pore_count = add_pore_marks(delta, point_region, pores, pore_density, pore_rng)
    else:
        pore_count = 0

    if color_variation > 0.0:
        tone_field = (
            1.0 * smooth_noise(tone_rng, width, height, 31)
            + 0.45 * smooth_noise(tone_rng, width, height, 11)
        )
        delta += color_variation * tone_field

    edited = source.astype(np.float32) + delta[..., None]
    actual_freckles = add_freckles(
        edited,
        point_region,
        freckles,
        freckle_opacity,
        freckle_color_jitter,
        freckle_rng,
    )
    alpha = mask.astype(np.float32)[..., None] / 255.0
    result = np.rint(source * (1.0 - alpha) + edited * alpha).clip(0, 255).astype(np.uint8)
    result[mask == 0] = source[mask == 0]
    return result, pore_count, actual_freckles


def save_comparison(original, result, path, result_label="Conventional texture prototype"):
    width, height = original.size
    canvas = Image.new("RGB", (width * 2, height + 32), (24, 24, 24))
    canvas.paste(original, (0, 32))
    canvas.paste(result, (width, 32))
    draw = ImageDraw.Draw(canvas)
    draw.text((10, 9), "Original", fill=(255, 255, 255))
    draw.text((width + 10, 9), result_label, fill=(255, 255, 255))
    canvas.save(path, format="PNG")


def load_effective_mask(mask_path, original, scope="classic"):
    if mask_path is None:
        raise ValueError("A reviewed mask PNG is required for processing.")
    if scope not in MASK_SCOPES:
        raise ValueError(f"Unknown mask scope: {scope}.")
    mask_path = mask_path.expanduser().resolve(strict=True)
    with Image.open(mask_path) as image:
        if image.size != original.size:
            raise ValueError(f"Mask size {image.size} does not match {original.size}.")
        user_mask = np.asarray(image.convert("L"), dtype=np.uint8).copy()
    if scope == "full-face":
        _, safe_mask, _, _ = build_full_face_mask(original.size)
    else:
        safe_mask = build_safe_mask(original.size)
    mask = np.minimum(user_mask, safe_mask)
    if not np.any(mask):
        raise ValueError(
            f"Reviewed mask has no editable pixels inside the safe {scope} area."
        )
    return mask_path, mask


def build_region_masks(mask, scope="classic"):
    if scope not in MASK_SCOPES:
        raise ValueError(f"Unknown mask scope: {scope}.")
    if scope == "full-face":
        return {"rostro_completo": mask.copy()}

    region_masks = {}
    combined = np.zeros_like(mask)
    for (name, _), polygon in zip(CROP_REGIONS, SKIN_POLYGONS):
        polygon_image = Image.new("L", (mask.shape[1], mask.shape[0]), 0)
        ImageDraw.Draw(polygon_image).polygon(polygon, fill=255)
        region_mask = np.minimum(mask, np.asarray(polygon_image, dtype=np.uint8))
        region_masks[name] = region_mask
        combined = np.maximum(combined, region_mask)
    if np.any((mask > 0) & (combined == 0)):
        raise ValueError("The approved mask contains editable pixels outside known skin regions.")
    return region_masks


def estimate_light_direction(luminance, region_mask):
    luminance_image = Image.fromarray(
        np.rint(luminance).clip(0, 255).astype(np.uint8), mode="L"
    )
    broad_illumination = np.asarray(
        luminance_image.filter(ImageFilter.GaussianBlur(radius=20.0)),
        dtype=np.float32,
    )
    gradient_y, gradient_x = np.gradient(broad_illumination)
    editable = region_mask > 0
    direction_x = float(np.mean(gradient_x[editable]))
    direction_y = float(np.mean(gradient_y[editable]))
    magnitude = math.hypot(direction_x, direction_y)
    if magnitude < 1e-4:
        return (-0.45, -0.89), True
    return (direction_x / magnitude, direction_y / magnitude), False


def build_relief_fields(source, region_masks, seed):
    source_array = np.asarray(source, dtype=np.float32)
    luminance = (
        source_array[..., 0] * 0.2126
        + source_array[..., 1] * 0.7152
        + source_array[..., 2] * 0.0722
    )
    region_seeds = np.random.SeedSequence(seed).spawn(len(region_masks))
    fields = {}
    for (name, region_mask), region_seed in zip(region_masks.items(), region_seeds):
        spec = RELIEF_REGION_SPECS[name]
        rng = np.random.default_rng(region_seed)
        height_field = np.zeros(region_mask.shape, dtype=np.float32)
        for spacing, weight in zip(spec["scales"], spec["weights"]):
            height_field += weight * smooth_noise(
                rng, region_mask.shape[1], region_mask.shape[0], spacing
            )
        height_field = normalize_noise(height_field)
        gradient_y, gradient_x = np.gradient(height_field)
        light_direction, used_fallback = estimate_light_direction(
            luminance, region_mask
        )
        directional_shading = -(
            gradient_x * light_direction[0] + gradient_y * light_direction[1]
        )
        directional_shading = normalize_noise(directional_shading)
        directional_shading = np.clip(directional_shading, -2.5, 2.5)

        feathered_mask = np.asarray(
            Image.fromarray(region_mask, mode="L").filter(
                ImageFilter.GaussianBlur(radius=1.5)
            ),
            dtype=np.float32,
        )
        alpha = np.minimum(feathered_mask, region_mask).astype(np.float32) / 255.0
        fields[name] = {
            "shading": directional_shading,
            "alpha": alpha,
            "gain": float(spec["gain"]),
            "light_direction": list(light_direction),
            "light_direction_fallback": used_fallback,
        }
    return fields


def apply_relief(source, mask, fields, intensity):
    if not 0.0 <= intensity <= 1.0:
        raise ValueError("Microrelief intensity must be between 0 and 1.")
    source_array = np.asarray(source, dtype=np.uint8)
    if intensity == 0.0:
        return source_array.copy()

    result = source_array.astype(np.float32)
    for field in fields.values():
        luminance_delta = (
            field["shading"] * field["gain"] * intensity * field["alpha"]
        )
        result += luminance_delta[..., None]
    result = np.rint(result).clip(0, 255).astype(np.uint8)
    result[mask == 0] = source_array[mask == 0]
    return result


def relief_contrast_metrics(source, result, region_masks):
    source_luminance = (
        np.asarray(source, dtype=np.float32)[..., 0] * 0.2126
        + np.asarray(source, dtype=np.float32)[..., 1] * 0.7152
        + np.asarray(source, dtype=np.float32)[..., 2] * 0.0722
    )
    result_array = np.asarray(result, dtype=np.float32)
    result_luminance = (
        result_array[..., 0] * 0.2126
        + result_array[..., 1] * 0.7152
        + result_array[..., 2] * 0.0722
    )

    def high_frequency_component(luminance):
        image = Image.fromarray(
            np.rint(luminance).clip(0, 255).astype(np.uint8), mode="L"
        )
        blurred = np.asarray(
            image.filter(ImageFilter.GaussianBlur(radius=3.0)),
            dtype=np.float32,
        )
        return luminance - blurred

    source_high = high_frequency_component(source_luminance)
    result_high = high_frequency_component(result_luminance)
    metrics = {}
    for name, region_mask in region_masks.items():
        editable = region_mask > 0
        before_std = float(np.std(source_luminance[editable]))
        after_std = float(np.std(result_luminance[editable]))
        before_microcontrast = float(np.std(source_high[editable]))
        after_microcontrast = float(np.std(result_high[editable]))
        metrics[name] = {
            "luminance_std_before": round(before_std, 4),
            "luminance_std_after": round(after_std, 4),
            "luminance_std_change": round(after_std - before_std, 4),
            "high_frequency_contrast_std_before": round(before_microcontrast, 4),
            "high_frequency_contrast_std_after": round(after_microcontrast, 4),
            "high_frequency_contrast_std_change": round(
                after_microcontrast - before_microcontrast, 4
            ),
            "luminance_delta_rms": round(
                float(np.sqrt(np.mean((result_luminance[editable] - source_luminance[editable]) ** 2))),
                4,
            ),
        }
    return metrics


def run_prototype(args, input_path, original):
    mask_path, mask = load_effective_mask(args.mask, original)
    run_dir = unique_directory(args.output_root, "texture_run")
    original.save(run_dir / "original.png", format="PNG")
    Image.fromarray(mask, mode="L").save(run_dir / "effective_mask.png")

    opacity_range = (args.freckle_opacity_min, args.freckle_opacity_max)
    start = time.perf_counter()
    result_array, pore_count, freckle_count = process_image(
        original,
        mask,
        args.pores,
        args.freckles,
        args.color_variation,
        args.seed,
        args.pore_density,
        opacity_range,
        args.freckle_color_jitter,
    )
    processing_seconds = time.perf_counter() - start

    zero_array, _, _ = process_image(original, mask, 0.0, 0, 0.0, args.seed)
    if not np.array_equal(zero_array, np.asarray(original)):
        raise AssertionError("Zero intensity did not reproduce the original pixels.")
    repeated_array, _, _ = process_image(
        original,
        mask,
        args.pores,
        args.freckles,
        args.color_variation,
        args.seed,
        args.pore_density,
        opacity_range,
        args.freckle_color_jitter,
    )
    if not np.array_equal(result_array, repeated_array):
        raise AssertionError("Same seed and controls produced different pixels.")

    source_array = np.asarray(original)
    changed = np.any(result_array != source_array, axis=2)
    outside_changed = int(np.count_nonzero(changed & (mask == 0)))
    if outside_changed != 0:
        raise AssertionError(f"{outside_changed} pixels changed outside the editable mask.")
    result = Image.fromarray(result_array, mode="RGB")
    result.save(run_dir / "result.png", format="PNG")
    save_comparison(original, result, run_dir / "comparison.png")

    summary = {
        "method": "conventional multiscale texture and procedural freckles; no generative AI",
        "input": input_path.name,
        "input_size": list(original.size),
        "output_size": list(result.size),
        "mask_source": str(mask_path),
        "editable_pixel_count": int(np.count_nonzero(mask)),
        "changed_pixel_count": int(np.count_nonzero(changed)),
        "changed_pixels_outside_mask": outside_changed,
        "pore_intensity": args.pores,
        "pore_density_multiplier": args.pore_density,
        "pore_marks_placed": pore_count,
        "freckle_count_requested": args.freckles,
        "freckle_marks_placed": freckle_count,
        "freckle_opacity_range": list(opacity_range),
        "freckle_color_jitter_levels": args.freckle_color_jitter,
        "color_variation": args.color_variation,
        "seed": args.seed,
        "processing_seconds": round(processing_seconds, 4),
        "zero_intensity_exact_match": True,
        "same_seed_identical": True,
        "result": "result.png",
        "mask": "effective_mask.png",
        "comparison": "comparison.png",
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(f"RUN_DIR={run_dir}")
    print(f"RESULT={run_dir / 'result.png'}")
    print(f"MASK={run_dir / 'effective_mask.png'}")
    print(f"COMPARISON={run_dir / 'comparison.png'}")
    print(f"PROCESSING_SECONDS={processing_seconds:.4f}")
    print(f"OUTPUT_SIZE={result.width}x{result.height}")
    print(f"PORE_MARKS={pore_count} FRECKLES={freckle_count}")
    print(f"CHANGED_PIXELS_OUTSIDE_MASK={outside_changed}")
    print("ZERO_INTENSITY_EXACT_MATCH=True SAME_SEED_IDENTICAL=True")


def save_crop_comparison(original, variants, region_name, box, path, scale=1):
    crops = [("Original", original.crop(box))]
    crops.extend((name.title(), image.crop(box)) for name, image in variants.items())
    if scale != 1:
        crops = [
            (
                label,
                crop.resize(
                    (crop.width * scale, crop.height * scale),
                    Image.Resampling.NEAREST,
                ),
            )
            for label, crop in crops
        ]
    crop_width, crop_height = crops[0][1].size
    title_height = 24
    label_height = 24
    canvas = Image.new(
        "RGB",
        (crop_width * 2, title_height + (crop_height + label_height) * 2),
        (24, 24, 24),
    )
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 4), region_name.replace("_", " ").title(), fill=(255, 255, 255))
    positions = (
        (0, title_height),
        (crop_width, title_height),
        (0, title_height + crop_height + label_height),
        (crop_width, title_height + crop_height + label_height),
    )
    for (label, crop), (x, y) in zip(crops, positions):
        draw.text((x + 8, y + 4), label, fill=(255, 255, 255))
        canvas.paste(crop, (x, y + label_height))
    canvas.save(path, format="PNG")


def save_inspection_mosaic(original, variants, path, scale=1):
    labels = [("Original", original)] + [
        (name.title(), image) for name, image in variants.items()
    ]
    max_width = max(box[2] - box[0] for _, box in CROP_REGIONS) * scale
    max_height = max(box[3] - box[1] for _, box in CROP_REGIONS) * scale
    region_header = 24
    label_height = 24
    row_height = region_header + label_height + max_height
    canvas = Image.new(
        "RGB",
        (max_width * len(labels), row_height * len(CROP_REGIONS)),
        (24, 24, 24),
    )
    draw = ImageDraw.Draw(canvas)
    for row, (region_name, box) in enumerate(CROP_REGIONS):
        row_y = row * row_height
        draw.text(
            (8, row_y + 4),
            f"{region_name.replace('_', ' ').title()} - {100 * scale}% crop",
            fill=(255, 255, 255),
        )
        crop_width = (box[2] - box[0]) * scale
        crop_height = (box[3] - box[1]) * scale
        for column, (label, image) in enumerate(labels):
            x = column * max_width
            draw.text((x + 8, row_y + region_header + 4), label, fill=(255, 255, 255))
            crop = image.crop(box)
            if scale != 1:
                crop = crop.resize(
                    (crop.width * scale, crop.height * scale),
                    Image.Resampling.NEAREST,
                )
            paste_x = x + (max_width - crop_width) // 2
            paste_y = row_y + region_header + label_height + (max_height - crop_height) // 2
            canvas.paste(crop, (paste_x, paste_y))
    canvas.save(path, format="PNG")


def sha256_file(path):
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_variants(args, input_path, original):
    mask_path, mask = load_effective_mask(args.mask, original)
    input_hash_before = sha256_file(input_path)
    mask_hash_before = sha256_file(mask_path)
    run_dir = unique_directory(args.output_root, "texture_variants")
    original.save(run_dir / "original.png", format="PNG")
    Image.fromarray(mask, mode="L").save(run_dir / "approved_mask.png")

    source_array = np.asarray(original)
    zero_array, _, _ = process_image(original, mask, 0.0, 0, 0.0, args.seed)
    if not np.array_equal(zero_array, source_array):
        raise AssertionError("Zero intensity did not reproduce the original pixels.")

    variant_images = {}
    variant_records = []
    for spec in VARIANT_SPECS:
        start = time.perf_counter()
        result_array, pore_count, freckle_count = process_image(
            original,
            mask,
            spec["pores"],
            spec["freckles"],
            spec["color_variation"],
            args.seed,
            spec["pore_density"],
            spec["freckle_opacity"],
            spec["freckle_color_jitter"],
        )
        processing_seconds = time.perf_counter() - start

        repeated_array, _, _ = process_image(
            original,
            mask,
            spec["pores"],
            spec["freckles"],
            spec["color_variation"],
            args.seed,
            spec["pore_density"],
            spec["freckle_opacity"],
            spec["freckle_color_jitter"],
        )
        if not np.array_equal(result_array, repeated_array):
            raise AssertionError(f"Variant {spec['name']} is not reproducible.")

        changed = np.any(result_array != source_array, axis=2)
        outside_changed = int(np.count_nonzero(changed & (mask == 0)))
        if outside_changed != 0:
            raise AssertionError(
                f"Variant {spec['name']} changed {outside_changed} pixels outside the mask."
            )

        result = Image.fromarray(result_array, mode="RGB")
        result.save(run_dir / f"result_{spec['name']}.png", format="PNG")
        save_comparison(
            original,
            result,
            run_dir / f"comparison_{spec['name']}.png",
            f"Conventional texture — {spec['name']}",
        )
        variant_images[spec["name"]] = result
        variant_records.append(
            {
                **spec,
                "freckle_opacity": list(spec["freckle_opacity"]),
                "pore_marks_placed": pore_count,
                "freckle_marks_placed": freckle_count,
                "processing_seconds": round(processing_seconds, 4),
                "changed_pixel_count": int(np.count_nonzero(changed)),
                "changed_pixels_outside_mask": outside_changed,
                "same_seed_identical": True,
            }
        )

    for region_name, box in CROP_REGIONS:
        save_crop_comparison(
            original,
            variant_images,
            region_name,
            box,
            run_dir / f"crop_{region_name}_100.png",
        )
    save_inspection_mosaic(
        original, variant_images, run_dir / "inspection_mosaic_100.png"
    )
    mosaic = Image.open(run_dir / "inspection_mosaic_100.png")
    try:
        mosaic.resize(
            (mosaic.width * 2, mosaic.height * 2), Image.Resampling.NEAREST
        ).save(run_dir / "inspection_mosaic_2x.png", format="PNG")
    finally:
        mosaic.close()

    input_hash_after = sha256_file(input_path)
    mask_hash_after = sha256_file(mask_path)
    if input_hash_before != input_hash_after or mask_hash_before != mask_hash_after:
        raise AssertionError("The original image or approved mask changed during processing.")

    summary = {
        "method": "conventional multiscale texture and procedural freckles; no generative AI",
        "input": input_path.name,
        "input_sha256_before": input_hash_before,
        "input_sha256_after": input_hash_after,
        "input_size": list(original.size),
        "approved_mask_path": str(mask_path),
        "approved_mask_sha256_before": mask_hash_before,
        "approved_mask_sha256_after": mask_hash_after,
        "editable_pixel_count": int(np.count_nonzero(mask)),
        "seed": args.seed,
        "zero_intensity_exact_match": True,
        "variants": variant_records,
        "crop_regions": {
            name: list(box) for name, box in CROP_REGIONS
        },
        "comparison_images": [
            "crop_frente_100.png",
            "crop_mejilla_izquierda_100.png",
            "crop_mejilla_derecha_100.png",
            "inspection_mosaic_100.png",
            "inspection_mosaic_2x.png",
        ],
        "mosaic_2x_note": "Nearest-neighbor enlargement for inspection only; results remain native resolution.",
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(f"RUN_DIR={run_dir}")
    for spec in VARIANT_SPECS:
        result_path = run_dir / f"result_{spec['name']}.png"
        print(f"RESULT_{spec['name'].upper()}={result_path}")
    print(f"MOSAIC={run_dir / 'inspection_mosaic_100.png'}")
    print(f"MOSAIC_2X={run_dir / 'inspection_mosaic_2x.png'}")
    print(f"SUMMARY={run_dir / 'summary.json'}")
    print(f"OUTPUT_SIZE={original.width}x{original.height}")
    print("ALL_OUTSIDE_MASK_PIXELS_UNCHANGED=True")
    print("ZERO_INTENSITY_EXACT_MATCH=True SAME_SEED_IDENTICAL=True")


def run_relief_variants(args, input_path, original):
    intensities = args.relief_intensities
    if not intensities or any(
        not math.isfinite(intensity) or not 0.0 <= intensity <= 1.0
        for intensity in intensities
    ):
        raise ValueError("--relief-intensities must contain values between 0 and 1.")
    if args.mask_scope == "full-face" and not any(
        math.isclose(intensity, 0.50, abs_tol=1e-9) for intensity in intensities
    ):
        raise ValueError(
            "Full-face mode requires intensity 0.50 for its requested comparison."
        )

    mask_path, mask = load_effective_mask(args.mask, original, args.mask_scope)
    input_hash_before = sha256_file(input_path)
    mask_hash_before = sha256_file(mask_path)
    region_masks = build_region_masks(mask, args.mask_scope)
    run_dir = unique_directory(args.output_root, "microrelief")
    original.save(run_dir / "original.png", format="PNG")
    Image.fromarray(mask, mode="L").save(run_dir / "approved_mask.png")
    for name, region_mask in region_masks.items():
        Image.fromarray(region_mask, mode="L").save(
            run_dir / f"region_mask_{name}.png"
        )

    source_array = np.asarray(original)
    fields = build_relief_fields(original, region_masks, args.seed)
    repeated_fields = build_relief_fields(original, region_masks, args.seed)
    for name in fields:
        if not np.array_equal(fields[name]["shading"], repeated_fields[name]["shading"]):
            raise AssertionError(f"Relief field for {name} is not reproducible.")
        if not np.array_equal(fields[name]["alpha"], repeated_fields[name]["alpha"]):
            raise AssertionError(f"Relief mask for {name} is not reproducible.")

    zero_array = apply_relief(original, mask, fields, 0.0)
    if not np.array_equal(zero_array, source_array):
        raise AssertionError("Zero microrelief intensity did not reproduce the original.")
    zero_path = run_dir / "result_relief_zero.png"
    Image.fromarray(zero_array, mode="RGB").save(zero_path, format="PNG")
    with Image.open(zero_path) as saved_zero:
        if not np.array_equal(np.asarray(saved_zero), source_array):
            raise AssertionError("Saved zero-intensity image differs from the original.")

    variant_images = {}
    variant_records = []
    for intensity in intensities:
        start = time.perf_counter()
        result_array = apply_relief(original, mask, fields, intensity)
        processing_seconds = time.perf_counter() - start
        repeated_array = apply_relief(original, mask, fields, intensity)
        if not np.array_equal(result_array, repeated_array):
            raise AssertionError(f"Microrelief intensity {intensity} is not reproducible.")

        changed = np.any(result_array != source_array, axis=2)
        outside_changed = int(np.count_nonzero(changed & (mask == 0)))
        if outside_changed != 0:
            raise AssertionError(
                f"Intensity {intensity} changed {outside_changed} pixels outside the mask."
            )

        intensity_label = f"{intensity:.2f}"
        intensity_token = f"{int(round(intensity * 100)):03d}"
        result_path = run_dir / f"result_relief_{intensity_token}.png"
        result_image = Image.fromarray(result_array, mode="RGB")
        result_image.save(result_path, format="PNG")
        variant_images[f"Intensity {intensity_label}"] = result_image
        variant_records.append(
            {
                "intensity": intensity,
                "result": result_path.name,
                "processing_seconds": round(processing_seconds, 4),
                "changed_pixel_count": int(np.count_nonzero(changed)),
                "changed_pixels_outside_mask": outside_changed,
                "same_seed_identical": True,
                "contrast": relief_contrast_metrics(
                    original, result_image, region_masks
                ),
            }
        )

    for region_name, box in CROP_REGIONS:
        save_crop_comparison(
            original,
            variant_images,
            region_name,
            box,
            run_dir / f"relief_crop_{region_name}_100.png",
        )
        save_crop_comparison(
            original,
            variant_images,
            region_name,
            box,
            run_dir / f"relief_crop_{region_name}_200.png",
            scale=2,
        )
    save_inspection_mosaic(
        original, variant_images, run_dir / "relief_mosaic_100.png"
    )
    save_inspection_mosaic(
        original, variant_images, run_dir / "relief_mosaic_200.png", scale=2
    )
    full_face_comparison = None
    if args.mask_scope == "full-face":
        medium_result = variant_images["Intensity 0.50"]
        full_face_comparison = run_dir / "full_face_comparison_050.png"
        save_comparison(
            original,
            medium_result,
            full_face_comparison,
            result_label="Microrelieve facial completo - intensidad 0.50",
        )

    input_hash_after = sha256_file(input_path)
    mask_hash_after = sha256_file(mask_path)
    if input_hash_before != input_hash_after or mask_hash_before != mask_hash_after:
        raise AssertionError("The original image or approved mask changed during processing.")

    summary = {
        "method": "conventional continuous multiscale synthetic microrelief; no generative AI",
        "mask_scope": args.mask_scope,
        "discrete_pore_marks": False,
        "new_freckles": False,
        "input": input_path.name,
        "input_sha256_before": input_hash_before,
        "input_sha256_after": input_hash_after,
        "input_size": list(original.size),
        "approved_mask_path": str(mask_path),
        "approved_mask_sha256_before": mask_hash_before,
        "approved_mask_sha256_after": mask_hash_after,
        "editable_pixel_count": int(np.count_nonzero(mask)),
        "region_masks": {
            name: {
                "editable_pixel_count": int(np.count_nonzero(region_mask)),
                "texture_scales_px": list(RELIEF_REGION_SPECS[name]["scales"]),
                "texture_weights": list(RELIEF_REGION_SPECS[name]["weights"]),
                "contrast_gain": RELIEF_REGION_SPECS[name]["gain"],
                "estimated_light_direction": fields[name]["light_direction"],
                "used_fallback_light_direction": fields[name][
                    "light_direction_fallback"
                ],
            }
            for name, region_mask in region_masks.items()
        },
        "seed": args.seed,
        "intensities": variant_records,
        "zero_intensity": {
            "exact_match": True,
            "result": zero_path.name,
        },
        "same_relief_field_scaled_by_intensity": True,
        "comparison_images": [
            "relief_mosaic_100.png",
            "relief_mosaic_200.png",
            *(
                ["full_face_comparison_050.png"]
                if full_face_comparison is not None
                else []
            ),
            *[
                f"relief_crop_{region_name}_{scale}.png"
                for region_name, _ in CROP_REGIONS
                for scale in ("100", "200")
            ],
        ],
        "200_percent_note": "Nearest-neighbor enlargement for viewing only; processing remains at original resolution.",
        "light_estimation_note": "A broad luminance blur is used only to estimate light direction; source pixels are never blurred.",
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(f"RUN_DIR={run_dir}")
    print(f"ZERO_INTENSITY={zero_path}")
    for record in variant_records:
        print(
            f"INTENSITY_{record['intensity']:.2f}="
            f"{run_dir / record['result']} "
            f"SECONDS={record['processing_seconds']:.4f} "
            f"CONTRAST={json.dumps(record['contrast'], separators=(',', ':'))}"
        )
    print(f"MOSAIC_100={run_dir / 'relief_mosaic_100.png'}")
    print(f"MOSAIC_200={run_dir / 'relief_mosaic_200.png'}")
    if full_face_comparison is not None:
        print(f"FULL_FACE_COMPARISON={full_face_comparison}")
    print(f"SUMMARY={run_dir / 'summary.json'}")
    print(f"OUTPUT_SIZE={original.width}x{original.height}")
    print("ALL_OUTSIDE_MASK_PIXELS_UNCHANGED=True")
    print("ZERO_INTENSITY_EXACT_MATCH=True SAME_SEED_IDENTICAL=True")


def main():
    args = parse_args()
    if args.mask_scope != "classic" and not args.run_relief:
        raise ValueError("--mask-scope is supported only with --run-relief.")
    input_path, original = load_original(args.input)
    if args.prepare_full_face_mask:
        if args.mask is not None:
            raise ValueError("--mask is not used while preparing a new full-face mask.")
        prepare_full_face_mask(original, input_path, args.output_root)
    elif args.run_relief:
        run_relief_variants(args, input_path, original)
    elif args.run_variants:
        run_variants(args, input_path, original)
    elif args.run:
        run_prototype(args, input_path, original)
    else:
        if args.mask is not None:
            raise ValueError(
                "--mask is used with a run mode; otherwise a suggested mask is prepared."
            )
        prepare_mask(original, args.output_root)


if __name__ == "__main__":
    main()
