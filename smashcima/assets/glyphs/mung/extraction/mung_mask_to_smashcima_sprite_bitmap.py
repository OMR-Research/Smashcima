import numpy as np


def mung_mask_to_smashcima_sprite_bitmap(mask: np.ndarray):
    """MuNG parses the symbol mask as a uint8 matrix with 0/1
    values (true/false). This method converts it into the black
    on transparent BGRA uint8 bitmap that smashcima sprites use."""
    assert len(mask.shape) == 2
    assert mask.dtype == np.uint8
    alpha = mask * 255
    color = np.zeros_like(mask)
    bitmap = np.stack([color, color, color, alpha], axis=2)
    return bitmap
