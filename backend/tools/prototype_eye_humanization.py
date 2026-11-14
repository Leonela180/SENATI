import argparse
import hashlib
import json
import shutil
import time
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = (
    ROOT
    / "private_data"
    / "results"
    / "eye_humanization"
    / "approved_skin_reference_20261113_211803.png"
)
DEFAULT_OUTPUT_ROOT = ROOT / "private_data" / "results" / "eye_humanization"
EXPECTED_SIZE = (1254, 1254)
PREVIEW_CROP_BOXES = {
    "left": (350, 320, 610, 485),
    "right": (644, 320, 904, 485),
}
LEFT_EYE_OPENING = (
    (368, 422),
    (381, 412),
    (399, 402),
    (419, 392),
    (440, 384),
    (461, 379),
    (482, 376),
    (503, 379),
    (522, 386),
    (542, 397),
    (559, 408),
    (576, 418),
    (587, 426),
    (579, 433),
    (562, 440),
    (541, 447),
    (519, 451),
    (496, 454),
    (474, 453),
    (450, 450),
    (429, 446),
    (408, 440),
    (390, 434),
    (376, 428),
)
LEFT_UPPER_LID_PROTECTION = (
    (368, 422),
    (379, 412),
    (398, 401),
    (418, 391),
    (440, 383),
    (461, 377),
    (483, 374),
    (504, 377),
    (525, 384),
    (546, 396),
    (565, 409),
    (586, 424),
    (580, 429),
    (561, 417),
    (542, 404),
    (523, 393),
    (503, 386),
    (483, 383),
    (462, 385),
    (441, 390),
    (420, 398),
    (402, 408),
    (385, 418),
    (374, 425),
)
LEFT_LOWER_LASH_PROTECTION = (
    (376, 428),
    (391, 434),
    (409, 440),
    (430, 446),
    (451, 450),
    (474, 453),
    (497, 454),
    (519, 451),
    (541, 447),
    (562, 440),
    (580, 432),
    (586, 436),
    (565, 445),
    (544, 452),
    (521, 457),
    (497, 460),
    (474, 459),
    (450, 456),
    (428, 452),
    (406, 446),
    (389, 440),
    (374, 434),
)
LEFT_WETLINE = (
    (405, 437),
    (425, 443),
    (445, 448),
    (465, 450),
    (485, 451),
    (505, 450),
    (525, 447),
    (545, 441),
    (560, 435),
    (557, 439),
    (540, 446),
    (522, 451),
    (503, 454),
    (484, 455),
    (465, 453),
    (445, 452),
    (425, 448),
    (407, 441),
)
LEFT_IRIS_BOX = (454, 386, 524, 451)
LEFT_PUPIL_BOX = (479, 408, 497, 429)
RIGHT_IRIS_BOX = (741, 386, 811, 451)
RIGHT_PUPIL_BOX = (768, 408, 786, 429)

COLORS = {
    "sclera_protected": (165, 100, 220),
    "eyelid_protected": (255, 155, 25),
    "iris_candidate": (35, 220, 80),
    "pupil_protected": (245, 55, 55),
    "reflection_candidate": (35, 220, 245),
    "wetline_candidate": (65, 125, 255),
}

PARAMETER_PROPOSAL = {
    "type": "Conventional local luminance processing; not generative AI",
    "color_policy": "Preserve brown hue and saturation; alter luminance only.",
    "levels": {
        "suave": {
            "iris_local_contrast": 0.03,
            "iris_existing_detail": 0.04,
            "existing_reflection_luminance": 0.02,
            "wetline_luminance": 0.01,
        },
        "equilibrada": {
            "iris_local_contrast": 0.06,
            "iris_existing_detail": 0.08,
            "existing_reflection_luminance": 0.04,
            "wetline_luminance": 0.02,
        },
        "visible": {
            "iris_local_contrast": 0.09,
            "iris_existing_detail": 0.12,
            "existing_reflection_luminance": 0.06,
            "wetline_luminance": 0.03,
        },
    },
    "constraints": [
        "Use only detail and catchlights already present in the source.",
        "Do not change pupil diameter, iris position, eye shape, or gaze.",
        "Do not brighten the sclera or add white highlights.",
        "Do not edit eyelids, eyelashes, eyebrows, skin, hair, nose, lips, or background.",
        "Keep all pixels outside the approved eye edit masks unchanged.",
        "Feather each edit mask inward by at most 1 px; do not expand it.",
    ],
    "status": "Proposal only; no eye enhancement has been applied.",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Prepare review-only eye masks or apply approved conventional eye detail."
        )
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--run",
        action="store_true",
        help="Create the three approved conventional eye-enhancement variants.",
    )
    parser.add_argument(
        "--mask-directory",
        type=Path,
        help="Directory containing the reviewed left/right eye masks.",
    )
    return parser.parse_args()


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_reference(path):
    path = path.expanduser().resolve(strict=True)
    with Image.open(path) as probe:
        image_format = probe.format
        probe.verify()
    if image_format != "PNG":
        raise ValueError("The approved eye reference must be a PNG.")
    with Image.open(path) as source:
        image = source.convert("RGB")
    if image.size != EXPECTED_SIZE:
        raise ValueError(f"Expected {EXPECTED_SIZE}, got {image.size}.")
    return path, image


def mirror_polygon(polygon):
    return tuple((EXPECTED_SIZE[0] - 1 - x, y) for x, y in polygon)


def draw_polygon(size, polygon):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).polygon(polygon, fill=255)
    return np.asarray(mask, dtype=np.uint8).copy()


def draw_ellipse(size, box):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).ellipse(box, fill=255)
    return np.asarray(mask, dtype=np.uint8).copy()


def feather_inward(mask, radius=1.0):
    blurred = np.asarray(
        Image.fromarray(mask, mode="L").filter(ImageFilter.GaussianBlur(radius)),
        dtype=np.uint8,
    )
    return np.minimum(mask, blurred)


def build_eye_masks(image):
    width, height = image.size
    eye_specs = {
        "left": {
            "opening": LEFT_EYE_OPENING,
            "upper_lid": LEFT_UPPER_LID_PROTECTION,
            "lower_lashes": LEFT_LOWER_LASH_PROTECTION,
            "wetline": LEFT_WETLINE,
            "iris_box": LEFT_IRIS_BOX,
            "pupil_box": LEFT_PUPIL_BOX,
        },
        "right": {
            "opening": mirror_polygon(LEFT_EYE_OPENING),
            "upper_lid": mirror_polygon(LEFT_UPPER_LID_PROTECTION),
            "lower_lashes": mirror_polygon(LEFT_LOWER_LASH_PROTECTION),
            "wetline": mirror_polygon(LEFT_WETLINE),
            "iris_box": RIGHT_IRIS_BOX,
            "pupil_box": RIGHT_PUPIL_BOX,
        },
    }
    image_array = np.asarray(image, dtype=np.uint8)
    luminance = (
        image_array[..., 0] * 0.2126
        + image_array[..., 1] * 0.7152
        + image_array[..., 2] * 0.0722
    )
    masks = {}
    for side, spec in eye_specs.items():
        opening = draw_polygon((width, height), spec["opening"])
        iris = np.minimum(
            draw_ellipse((width, height), spec["iris_box"]), opening
        )
        pupil = np.minimum(
            draw_ellipse((width, height), spec["pupil_box"]), iris
        )
        upper_lid = draw_polygon((width, height), spec["upper_lid"])
        lower_lashes = draw_polygon((width, height), spec["lower_lashes"])
        eyelid_protection = np.maximum(upper_lid, lower_lashes)
        wetline = draw_polygon((width, height), spec["wetline"])

        if side == "left":
            reflection_search = draw_ellipse((width, height), (490, 405, 509, 424))
        else:
            reflection_search = draw_ellipse((width, height), (798, 405, 812, 426))
        low_chroma = (
            image_array.max(axis=2).astype(np.int16)
            - image_array.min(axis=2).astype(np.int16)
        ) <= 95
        existing_reflections = (
            (iris > 0)
            & (reflection_search > 0)
            & (luminance >= 145.0)
            & low_chroma
        ).astype(np.uint8) * 255

        pupil_protection = np.minimum(pupil, 255 - existing_reflections)
        iris_edit = iris.copy()
        iris_edit[pupil > 0] = 0
        iris_edit[existing_reflections > 0] = 0
        iris_edit[eyelid_protection > 0] = 0

        wetline[iris > 0] = 0
        wetline[pupil > 0] = 0
        wetline[eyelid_protection > 0] = 0
        wetline = np.minimum(wetline, opening)

        active = np.maximum.reduce((iris_edit, existing_reflections, wetline))
        protected_in_eye = np.minimum(opening, 255 - active)
        sclera_protection = protected_in_eye.copy()
        sclera_protection[iris > 0] = 0
        sclera_protection[pupil_protection > 0] = 0
        sclera_protection[eyelid_protection > 0] = 0
        sclera_protection[wetline > 0] = 0

        masks[side] = {
            "eye_edit": feather_inward(active),
            "iris_detail": feather_inward(iris_edit),
            "existing_reflections": feather_inward(existing_reflections),
            "wetline": feather_inward(wetline),
            "pupil_protection": pupil_protection,
            "eyelid_protection": eyelid_protection,
            "sclera_protection": sclera_protection,
            "eye_opening": opening,
        }
    return masks


def overlay_mask(image_array, mask, color, strength):
    alpha = (mask.astype(np.float32) / 255.0 * strength)[..., None]
    color_array = np.asarray(color, dtype=np.float32)
    return image_array * (1.0 - alpha) + color_array * alpha


def preview_array(image, side_masks):
    preview = np.asarray(image, dtype=np.float32).copy()
    return overlay_component_masks(preview, side_masks)


def overlay_component_masks(preview, side_masks):
    draw_order = (
        ("sclera_protection", "sclera_protected", 0.35),
        ("eyelid_protection", "eyelid_protected", 0.58),
        ("iris_detail", "iris_candidate", 0.45),
        ("pupil_protection", "pupil_protected", 0.68),
        ("wetline", "wetline_candidate", 0.72),
        ("existing_reflections", "reflection_candidate", 0.85),
    )
    for mask_name, color_name, strength in draw_order:
        preview = overlay_mask(
            preview, side_masks[mask_name], COLORS[color_name], strength
        )
    return preview


def save_preview(image, masks, path):
    canvas_height = image.height + 94
    canvas = Image.new("RGB", (image.width, canvas_height), (24, 27, 31))
    combined = np.asarray(image, dtype=np.float32).copy()
    for side_masks in masks.values():
        combined = overlay_component_masks(combined, side_masks)
    canvas.paste(
        Image.fromarray(np.rint(combined).clip(0, 255).astype(np.uint8)),
        (0, 94),
    )

    draw = ImageDraw.Draw(canvas)
    draw.text((12, 8), "VISTA PREVIA - SIN PROCESAR LA IMAGEN", fill=(255, 255, 255))
    legend = (
        ("iris_candidate", "IRIS CANDIDATO"),
        ("reflection_candidate", "REFLEJOS EXISTENTES"),
        ("wetline_candidate", "ZONA HUMEDA"),
        ("pupil_protected", "PUPILA PROTEGIDA"),
        ("eyelid_protected", "PARPADOS / PESTANAS PROTEGIDOS"),
        ("sclera_protected", "ESCLERA PROTEGIDA"),
    )
    x = 12
    y = 37
    for index, (color_name, label) in enumerate(legend):
        if index == 3:
            x = 12
            y = 63
        draw.rectangle((x, y, x + 16, y + 16), fill=COLORS[color_name])
        draw.text((x + 21, y + 2), label, fill=(245, 245, 245))
        x += 28 + len(label) * 6
    canvas.save(path, format="PNG")


def save_eye_crop_preview(image, masks, side, path):
    box = PREVIEW_CROP_BOXES[side]
    source = np.asarray(image.crop(box), dtype=np.float32)
    crop_masks = {
        name: mask[box[1] : box[3], box[0] : box[2]]
        for name, mask in masks[side].items()
    }
    preview = preview_array(Image.fromarray(source.astype(np.uint8)), crop_masks)
    crop = Image.fromarray(
        np.rint(preview).clip(0, 255).astype(np.uint8)
    ).resize(
        ((box[2] - box[0]) * 2, (box[3] - box[1]) * 2),
        Image.Resampling.LANCZOS,
    )
    crop.save(path, format="PNG")


def create_review_directory(root, prefix="eye_mask_review"):
    root.mkdir(parents=True, exist_ok=True)
    base = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    candidate = root / base
    suffix = 1
    while candidate.exists():
        candidate = root / f"{base}_{suffix}"
        suffix += 1
    candidate.mkdir()
    return candidate


def prepare_masks(input_path, output_root):
    input_path, image = load_reference(input_path)
    input_hash_before = sha256_file(input_path)
    masks = build_eye_masks(image)
    review_dir = create_review_directory(output_root)
    for side, side_masks in masks.items():
        for name, mask in side_masks.items():
            Image.fromarray(mask, mode="L").save(
                review_dir / f"{side}_{name}_mask.png"
            )
    save_preview(image, masks, review_dir / "eye_masks_preview.png")
    for side in masks:
        save_eye_crop_preview(
            image, masks, side, review_dir / f"{side}_eye_preview_200.png"
        )

    input_hash_after = sha256_file(input_path)
    if input_hash_before != input_hash_after:
        raise AssertionError("The approved skin reference changed during mask preparation.")
    details = {
        "input": str(input_path),
        "input_sha256_before": input_hash_before,
        "input_sha256_after": input_hash_after,
        "input_size": list(image.size),
        "mask_pixel_counts": {
            side: {
                name: int(np.count_nonzero(mask))
                for name, mask in side_masks.items()
            }
            for side, side_masks in masks.items()
        },
        "left_eye_mask": "left_eye_edit_mask.png",
        "right_eye_mask": "right_eye_edit_mask.png",
        "component_masks_per_eye": [
            "iris_detail",
            "existing_reflections",
            "wetline",
            "pupil_protection",
            "eyelid_protection",
            "sclera_protection",
        ],
        "proposal": PARAMETER_PROPOSAL,
        "review_note": "Masks and parameter proposal only. No eye changes have been applied.",
    }
    (review_dir / "eye_mask_review.json").write_text(
        json.dumps(details, indent=2), encoding="utf-8"
    )
    print(f"REFERENCE={input_path}")
    print(f"REFERENCE_SHA256={input_hash_before}")
    print(f"MASK_PREVIEW={review_dir / 'eye_masks_preview.png'}")
    print(f"LEFT_CROP={review_dir / 'left_eye_preview_200.png'}")
    print(f"RIGHT_CROP={review_dir / 'right_eye_preview_200.png'}")
    print(f"PARAMETERS={review_dir / 'eye_mask_review.json'}")
    print("NO_EYE_ENHANCEMENT_APPLIED=True")
    return review_dir


def load_approved_masks(mask_directory, image_size):
    mask_directory = Path(mask_directory).expanduser().resolve(strict=True)
    masks = {}
    hashes = {}
    for side in ("left", "right"):
        side_masks = {}
        for name in (
            "eye_edit",
            "iris_detail",
            "existing_reflections",
            "wetline",
            "pupil_protection",
            "eyelid_protection",
            "sclera_protection",
            "eye_opening",
        ):
            path = mask_directory / f"{side}_{name}_mask.png"
            with Image.open(path) as source:
                if source.size != image_size:
                    raise ValueError(f"Mask size {source.size} does not match {image_size}.")
                side_masks[name] = np.asarray(source.convert("L"), dtype=np.uint8).copy()
            hashes[str(path)] = sha256_file(path)

        edit_mask = side_masks["eye_edit"]
        opening = side_masks["eye_opening"] > 0
        if not np.any(edit_mask):
            raise ValueError(f"The approved {side} eye mask has no editable pixels.")
        if np.any((edit_mask > 0) & ~opening):
            raise ValueError(f"The approved {side} eye edit mask extends outside the eye.")
        if np.any(
            (edit_mask > 0) & (side_masks["pupil_protection"] > 0)
        ):
            raise ValueError(f"The approved {side} eye mask overlaps the pupil protection.")
        for protection_name in ("eyelid_protection", "sclera_protection"):
            if np.any(
                (edit_mask > 0) & (side_masks[protection_name] > 0)
            ):
                raise ValueError(
                    f"The approved {side} eye mask overlaps {protection_name}."
                )
        masks[side] = side_masks
    if np.any((masks["left"]["eye_edit"] > 0) & (masks["right"]["eye_edit"] > 0)):
        raise ValueError("The left and right eye edit masks overlap.")
    return mask_directory, masks, hashes


def luminance_array(source):
    source_array = np.asarray(source, dtype=np.float32)
    return (
        source_array[..., 0] * 0.2126
        + source_array[..., 1] * 0.7152
        + source_array[..., 2] * 0.0722
    )


def blurred_luminance(luminance, radius):
    image = Image.fromarray(
        np.rint(luminance).clip(0, 255).astype(np.uint8), mode="L"
    )
    return np.asarray(
        image.filter(ImageFilter.GaussianBlur(radius=radius)), dtype=np.float32
    )


def apply_eye_enhancement(image, masks, level_name):
    source = np.asarray(image, dtype=np.uint8)
    if level_name == "zero":
        return source.copy()
    if level_name not in PARAMETER_PROPOSAL["levels"]:
        raise ValueError(f"Unknown eye intensity: {level_name}.")

    level = PARAMETER_PROPOSAL["levels"][level_name]
    luminance = luminance_array(source)
    iris_contrast = luminance - blurred_luminance(luminance, radius=3.0)
    iris_detail = luminance - blurred_luminance(luminance, radius=1.0)
    reflection_detail = np.maximum(
        luminance - blurred_luminance(luminance, radius=6.0), 0.0
    )
    wetline_detail = np.maximum(
        luminance - blurred_luminance(luminance, radius=2.0), 0.0
    )
    delta = np.zeros(luminance.shape, dtype=np.float32)

    for side_masks in masks.values():
        iris_alpha = side_masks["iris_detail"].astype(np.float32) / 255.0
        reflection_alpha = (
            side_masks["existing_reflections"].astype(np.float32) / 255.0
        )
        wetline_alpha = side_masks["wetline"].astype(np.float32) / 255.0
        delta += iris_alpha * (
            level["iris_local_contrast"] * iris_contrast
            + level["iris_existing_detail"] * iris_detail
        )
        delta += (
            reflection_alpha
            * level["existing_reflection_luminance"]
            * reflection_detail
        )
        delta += wetline_alpha * level["wetline_luminance"] * wetline_detail

    common_shift = np.rint(np.clip(delta, -4.0, 4.0)).astype(np.int16)
    source_int16 = source.astype(np.int16)
    lower_bound = -source_int16.min(axis=2)
    upper_bound = 255 - source_int16.max(axis=2)
    common_shift = np.minimum(
        np.maximum(common_shift, lower_bound), upper_bound
    )
    result = np.clip(
        source_int16 + common_shift[..., None], 0, 255
    ).astype(np.uint8)
    combined_edit_mask = np.maximum.reduce(
        [side_masks["eye_edit"] for side_masks in masks.values()]
    )
    result[combined_edit_mask == 0] = source[combined_edit_mask == 0]
    return result


def save_eye_comparison_sheet(original, variants, scale, path):
    labels = (
        ("Original", original),
        ("Suave", variants["suave"]),
        ("Equilibrada", variants["equilibrada"]),
        ("Visible", variants["visible"]),
    )
    first_box = PREVIEW_CROP_BOXES["left"]
    crop_width = (first_box[2] - first_box[0]) * scale
    crop_height = (first_box[3] - first_box[1]) * scale
    section_height = 22 + 22 + crop_height
    canvas = Image.new(
        "RGB",
        (crop_width * len(labels), 28 + 2 * section_height),
        (24, 27, 31),
    )
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 6), f"Comparacion de ojos - {scale * 100}%", fill=(255, 255, 255))
    for row, side in enumerate(("left", "right")):
        row_top = 28 + row * section_height
        draw.text(
            (8, row_top + 4),
            "Ojo izquierdo" if side == "left" else "Ojo derecho",
            fill=(255, 255, 255),
        )
        box = PREVIEW_CROP_BOXES[side]
        for column, (label, image) in enumerate(labels):
            crop = image.crop(box)
            if scale != 1:
                crop = crop.resize(
                    (crop.width * scale, crop.height * scale),
                    Image.Resampling.NEAREST,
                )
            x = column * crop_width
            y = row_top + 22
            draw.text((x + 6, y + 3), label, fill=(255, 255, 255))
            canvas.paste(crop, (x, y + 22))
    canvas.save(path, format="PNG")


def run_eye_variants(input_path, output_root, mask_directory):
    input_path, original = load_reference(input_path)
    input_hash_before = sha256_file(input_path)
    mask_directory, masks, mask_hashes_before = load_approved_masks(
        mask_directory, original.size
    )
    run_dir = create_review_directory(output_root, prefix="eye_humanization")
    for side, side_masks in masks.items():
        for name, mask in side_masks.items():
            Image.fromarray(mask, mode="L").save(
                run_dir / f"{side}_{name}_mask_used.png"
            )

    zero_result = apply_eye_enhancement(original, masks, "zero")
    if not np.array_equal(zero_result, np.asarray(original)):
        raise AssertionError("Zero eye intensity did not reproduce the reference.")
    zero_path = run_dir / "result_eye_zero.png"
    Image.fromarray(zero_result, mode="RGB").save(zero_path, format="PNG")
    with Image.open(zero_path) as saved_zero:
        if not np.array_equal(np.asarray(saved_zero), np.asarray(original)):
            raise AssertionError("Saved zero-intensity image differs from the reference.")

    variants = {}
    records = []
    source = np.asarray(original, dtype=np.uint8)
    combined_mask = np.maximum.reduce(
        [side_masks["eye_edit"] for side_masks in masks.values()]
    )
    for level_name in ("suave", "equilibrada", "visible"):
        start = time.perf_counter()
        result_array = apply_eye_enhancement(original, masks, level_name)
        elapsed = time.perf_counter() - start
        repeated = apply_eye_enhancement(original, masks, level_name)
        if not np.array_equal(result_array, repeated):
            raise AssertionError(f"Eye intensity {level_name} is not reproducible.")

        changed = np.any(result_array != source, axis=2)
        outside_changed = int(np.count_nonzero(changed & (combined_mask == 0)))
        if outside_changed:
            raise AssertionError(
                f"Intensity {level_name} changed {outside_changed} pixels outside the eye masks."
            )
        result_image = Image.fromarray(result_array, mode="RGB")
        variants[level_name] = result_image
        result_path = run_dir / f"result_eye_{level_name}.png"
        result_image.save(result_path, format="PNG")
        luminance_delta = np.abs(
            luminance_array(result_array) - luminance_array(source)
        )
        records.append(
            {
                "level": level_name,
                "result": result_path.name,
                "processing_seconds": round(elapsed, 4),
                "changed_pixel_count": int(np.count_nonzero(changed)),
                "changed_pixels_outside_eye_masks": outside_changed,
                "maximum_luminance_change": float(luminance_delta.max()),
                "same_run_identical": True,
            }
        )

    comparison_paths = {}
    for scale in (1, 2):
        filename = f"eye_comparison_{scale * 100}.png"
        save_eye_comparison_sheet(
            original, variants, scale, run_dir / filename
        )
        comparison_paths[str(scale * 100)] = filename

    input_hash_after = sha256_file(input_path)
    mask_hashes_after = {
        path: sha256_file(Path(path)) for path in mask_hashes_before
    }
    if input_hash_before != input_hash_after:
        raise AssertionError("The approved skin reference changed during processing.")
    if mask_hashes_before != mask_hashes_after:
        raise AssertionError("An approved eye mask changed during processing.")

    summary = {
        "method": "Conventional local luminance enhancement; no generative AI",
        "input": str(input_path),
        "input_size": list(original.size),
        "input_sha256_before": input_hash_before,
        "input_sha256_after": input_hash_after,
        "mask_directory": str(mask_directory),
        "mask_sha256_before": mask_hashes_before,
        "mask_sha256_after": mask_hashes_after,
        "eye_masks": {
            side: {
                "editable_pixel_count": int(
                    np.count_nonzero(side_masks["eye_edit"])
                )
            }
            for side, side_masks in masks.items()
        },
        "color_policy": "A common integer luminance shift is applied equally to RGB channels.",
        "eye_shape_and_gaze_changed": False,
        "new_reflections_added": False,
        "outside_eye_masks_changed": False,
        "zero_intensity_exact_match": True,
        "same_input_and_masks_reproducible": True,
        "parameter_levels": PARAMETER_PROPOSAL["levels"],
        "variants": records,
        "comparisons": comparison_paths,
        "review_note": "Conventional processing only; visual naturalness still requires human review.",
    }
    (run_dir / "eye_humanization_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(f"RUN_DIR={run_dir}")
    print(f"ZERO_INTENSITY={zero_path}")
    for record in records:
        print(
            f"INTENSITY_{record['level'].upper()}={run_dir / record['result']} "
            f"SECONDS={record['processing_seconds']:.4f} "
            f"CHANGED={record['changed_pixel_count']} "
            f"OUTSIDE_MASK={record['changed_pixels_outside_eye_masks']}"
        )
    for scale, filename in comparison_paths.items():
        print(f"COMPARISON_{scale}={run_dir / filename}")
    print(f"SUMMARY={run_dir / 'eye_humanization_summary.json'}")
    print(f"OUTPUT_SIZE={original.width}x{original.height}")
    print("NO_CHANGES_OUTSIDE_EYE_MASKS=True ZERO_INTENSITY_EXACT_MATCH=True")
    return run_dir


def main():
    args = parse_args()
    if args.run:
        if args.mask_directory is None:
            raise ValueError("--run requires --mask-directory with reviewed eye masks.")
        run_eye_variants(args.input, args.output_root, args.mask_directory)
    else:
        if args.mask_directory is not None:
            raise ValueError("--mask-directory is only used with --run.")
        prepare_masks(args.input, args.output_root)


if __name__ == "__main__":
    main()
