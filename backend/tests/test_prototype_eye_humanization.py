import importlib.util
from pathlib import Path

import numpy as np
import pytest
from PIL import Image


SCRIPT_PATH = Path(__file__).parents[1] / "tools" / "prototype_eye_humanization.py"
SPEC = importlib.util.spec_from_file_location("prototype_eye_humanization", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
eye_prototype = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(eye_prototype)


@pytest.mark.skipif(not eye_prototype.DEFAULT_INPUT.exists(),
                    reason="Imagen de referencia privada ausente (private_data no se sube a GitHub)")
def test_eye_edit_masks_are_separate_and_confined_to_eye_components():
    _, image = eye_prototype.load_reference(eye_prototype.DEFAULT_INPUT)
    masks = eye_prototype.build_eye_masks(image)
    left = masks["left"]
    right = masks["right"]

    assert np.count_nonzero(left["eye_edit"]) > 0
    assert np.count_nonzero(right["eye_edit"]) > 0
    assert np.count_nonzero(left["existing_reflections"]) > 0
    assert np.count_nonzero(right["existing_reflections"]) > 0
    assert not np.any((left["eye_edit"] > 0) & (right["eye_edit"] > 0))

    for side_masks in masks.values():
        outside_opening = side_masks["eye_opening"] == 0
        assert np.all(side_masks["eye_edit"][outside_opening] == 0)
        assert np.all(side_masks["eye_edit"][side_masks["pupil_protection"] > 0] == 0)


def test_eye_enhancement_is_deterministic_and_changes_only_approved_masks():
    rng = np.random.default_rng(42)
    luminance = rng.integers(80, 140, size=(64, 64), dtype=np.uint8)
    pixels = np.stack(
        (luminance + 20, luminance, luminance - 20), axis=-1
    ).astype(np.uint8)
    original = Image.fromarray(pixels, mode="RGB")
    eye_edit = np.zeros((64, 64), dtype=np.uint8)
    eye_edit[12:52, 12:52] = 255
    iris_detail = np.zeros_like(eye_edit)
    iris_detail[18:46, 18:46] = 255
    reflections = np.zeros_like(eye_edit)
    reflections[25:28, 29:32] = 255
    wetline = np.zeros_like(eye_edit)
    wetline[46:49, 20:44] = 255
    blank = np.zeros_like(eye_edit)
    masks = {
        "left": {
            "eye_edit": eye_edit,
            "iris_detail": iris_detail,
            "existing_reflections": reflections,
            "wetline": wetline,
        },
        "right": {
            "eye_edit": blank,
            "iris_detail": blank,
            "existing_reflections": blank,
            "wetline": blank,
        },
    }

    zero_result = eye_prototype.apply_eye_enhancement(original, masks, "zero")
    result = eye_prototype.apply_eye_enhancement(original, masks, "equilibrada")
    repeated = eye_prototype.apply_eye_enhancement(
        original, masks, "equilibrada"
    )

    np.testing.assert_array_equal(zero_result, pixels)
    np.testing.assert_array_equal(result, repeated)
    np.testing.assert_array_equal(result[eye_edit == 0], pixels[eye_edit == 0])
    assert np.any(result != pixels)
    np.testing.assert_array_equal(
        result[..., 0].astype(np.int16) - result[..., 1].astype(np.int16),
        pixels[..., 0].astype(np.int16) - pixels[..., 1].astype(np.int16),
    )
