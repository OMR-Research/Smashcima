from typing import Callable, Dict, List, Optional, Tuple

import cv2
import numpy as np
from mung.node import Node

from smashcima.geometry import Point, Vector2
from smashcima.scene import ComposedGlyph, Glyph, LineGlyph, ScenePoint, Sprite
from smashcima.scene.AffineSpace import AffineSpace
from smashcima.scene.SmashcimaLabels import SmashcimaLabels
from smashcima.scene.SmuflLabels import SmuflLabels

from ..mung.MungGlyphMetadata import MungGlyphMetadata
from ..mung.MungDocument import MungDocument

# source:
# https://pages.cvc.uab.es/cvcmuscima/index_database.html
MUSCIMA_PP_DPI = 300 # TODO: get DPI per page

# TODO: change to millimeters?
TALL_BARLINE_THRESHOLD_PX = 150
BEAM_HOOK_MAX_WIDTH_PX = 25


def _mpp_mask_to_sprite_bitmap(mask: np.ndarray):
    """True/False pixel mask to black on transparent BGRA uint8 bitmap"""
    assert len(mask.shape) == 2
    assert mask.dtype == np.uint8
    alpha = mask * 255
    color = np.zeros_like(mask)
    bitmap = np.stack([color, color, color, alpha], axis=2)
    return bitmap


def _crop_objects_to_single_sprite_glyphs(
    nodes: List[Node],
    page: MungDocument,
    label: str,
    sprite_origin: Optional[Callable[[Node], Point]] = None
) -> List[Glyph]:
    glyphs: List[Glyph] = []

    for node in nodes:
        space = AffineSpace()
        sprite = Sprite(
            space=space,
            bitmap=_mpp_mask_to_sprite_bitmap(node.mask),
            bitmap_origin=(
                sprite_origin(node) if sprite_origin else Point(0.5, 0.5)
            ),
            dpi=MUSCIMA_PP_DPI
        )
        glyph = Glyph(
            space=space,
            region=Glyph.build_region_from_sprites_alpha_channel(
                label=label,
                sprites=[sprite]
            ),
            sprites=[sprite]
        )
        page.stamp_glyph(glyph, node)
        glyphs.append(glyph)

    return glyphs


################################################
# Code that actually extracts required symbols #
################################################


def get_full_noteheads(page: MungDocument) -> List[Glyph]:
    return _crop_objects_to_single_sprite_glyphs(
        nodes=[
            n for n in page.nodes
            if n.class_name == "noteheadFull"
            and not page.has_outlink_to(n, "legerLine")
        ],
        page=page,
        label=SmuflLabels.noteheadBlack.value
    )
