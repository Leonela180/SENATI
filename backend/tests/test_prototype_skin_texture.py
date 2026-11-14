import importlib.util
from pathlib import Path

import numpy as np
from PIL import Image


SCRIPT_PATH = Path(__file__).parents[1] / "tools" / "prototype_skin_texture.py"
SPEC = importlib.util.spec_from_file_location("prototype_skin_texture", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
skin_texture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(skin_texture)


def test_classic_mask_scope_preserves_existing_intersection(tmp_path):
    user_mask = np.full(skin_texture.EXPECTED_SIZE[::-1], 200, dtype=np.uint8)
    user_mask[200, 200] = 0
    mask_path = tmp_path / "classic_mask.png"
    Image.fromarray(user_mask, mode="L").save(mask_path)
    original = Image.new("RGB", skin_texture.EXPECTED_SIZE)

    _, default_mask = skin_texture.load_effective_mask(mask_path, original)
    _, explicit_mask = skin_texture.load_effective_mask(
        mask_path, original, scope="classic"
    )
    expected = np.minimum(user_mask, skin_texture.build_safe_mask(original.size))

    np.testing.assert_array_equal(default_mask, expected)
    np.testing.assert_array_equal(explicit_mask, expected)
    classic_regions = skin_texture.build_region_masks(
        skin_texture.build_safe_mask(original.size)
    )
    assert tuple(classic_regions) == tuple(
        name for name, _ in skin_texture.CROP_REGIONS
    )


def test_full_face_scope_uses_reviewed_gradient_and_feature_protections(tmp_path):
    _, reviewed_mask, protected, _ = skin_texture.build_full_face_mask(
        skin_texture.EXPECTED_SIZE
    )
    mask_path = tmp_path / "full_face_mask.png"
    Image.fromarray(reviewed_mask, mode="L").save(mask_path)
    original = Image.new("RGB", skin_texture.EXPECTED_SIZE)

    _, full_face_mask = skin_texture.load_effective_mask(
        mask_path, original, scope="full-face"
    )
    _, classic_mask = skin_texture.load_effective_mask(mask_path, original)

    np.testing.assert_array_equal(full_face_mask, reviewed_mask)
    assert np.all(full_face_mask[protected > 0] == 0)
    assert np.any((full_face_mask > 0) & (full_face_mask < 255))
    for point in ((627, 200), (340, 390), (627, 600), (627, 950)):
        x, y = point
        assert full_face_mask[y, x] > 0
    for point in ((340, 390), (627, 600), (627, 950)):
        x, y = point
        assert classic_mask[y, x] == 0


def test_full_face_relief_is_one_reproducible_region_and_preserves_zero_pixels():
    height, width = 96, 96
    mask = np.full((height, width), 255, dtype=np.uint8)
    mask[:, 0] = 0
    mask[:, 1] = 64
    mask[:, 2] = 128
    mask[:, 3] = 192
    regions = skin_texture.build_region_masks(mask, scope="full-face")
    assert list(regions) == ["rostro_completo"]
    np.testing.assert_array_equal(regions["rostro_completo"], mask)

    y, x = np.indices((height, width))
    pixels = np.stack((80 + x, 90 + y, 100 + (x + y) // 2), axis=-1).astype(
        np.uint8
    )
    original = Image.fromarray(pixels, mode="RGB")
    fields = skin_texture.build_relief_fields(original, regions, seed=1234)
    repeated_fields = skin_texture.build_relief_fields(original, regions, seed=1234)
    np.testing.assert_array_equal(
        fields["rostro_completo"]["shading"],
        repeated_fields["rostro_completo"]["shading"],
    )
    np.testing.assert_array_equal(
        fields["rostro_completo"]["alpha"],
        repeated_fields["rostro_completo"]["alpha"],
    )

    zero_result = skin_texture.apply_relief(original, mask, fields, intensity=0.0)
    np.testing.assert_array_equal(zero_result, pixels)
    result = skin_texture.apply_relief(original, mask, fields, intensity=0.5)
    repeated_result = skin_texture.apply_relief(
        original, mask, repeated_fields, intensity=0.5
    )
    np.testing.assert_array_equal(result, repeated_result)
    np.testing.assert_array_equal(result[mask == 0], pixels[mask == 0])
    assert result.shape == (height, width, 3)
