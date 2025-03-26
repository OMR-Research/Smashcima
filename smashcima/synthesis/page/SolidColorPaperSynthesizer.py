from smashcima.scene.AffineSpace import AffineSpace
from smashcima.scene.Sprite import Sprite
from smashcima.geometry.Rectangle import Rectangle
from smashcima.geometry.Transform import Transform
from smashcima.geometry.Point import Point
from smashcima.geometry.Vector2 import Vector2
from ..PaperSynthesizer import PaperSynthesizer
from smashcima.geometry.units import mm_to_px
from typing import Tuple
import numpy as np


COLOR_WHITE = (255, 255, 255, 255)
COLOR_TRANSPARENT = (0, 0, 0, 0)


class SolidColorPaperSynthesizer(PaperSynthesizer):
    def __init__(self):
        self.color: Tuple[int, int, int, int] = COLOR_WHITE
        "Color to use as the paper, BGRA uint8 format"

        self.dpi = 72
        "The DPI at which to rasterize the sprite"

    def synthesize_paper(
        self,
        page_space: AffineSpace,
        placement: Rectangle
    ):
        # width_px
        img = np.empty(
            shape=(
                int(mm_to_px(placement.height, self.dpi)),
                int(mm_to_px(placement.width, self.dpi)),
                4
            ),
            dtype=np.uint8
        )
        img[:,:] = self.color
        
        # create the sprite scene object
        Sprite(
            space=page_space,
            bitmap=img,
            bitmap_origin=Point(0, 0),
            dpi=self.dpi,
            transform=Transform.translate(Vector2(placement.x, placement.y))
        )
