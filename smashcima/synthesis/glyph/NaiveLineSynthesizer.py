import cv2
import numpy as np

from smashcima.geometry import Point, Rectangle, Transform, Vector2
from smashcima.scene import Glyph, LineGlyph, ScenePoint, Sprite, AffineSpace

from ..LineSynthesizer import LineSynthesizer


class NaiveLineSynthesizer(LineSynthesizer):
    def __init__(self, color=(0, 0, 0, 255), line_width=0.5, dpi=300):
        self.color = color
        "Color of the lines"
        
        self.line_width = line_width
        "The width of the synthesized naive line"

        self.dpi = dpi
        "DPI at which to synthesize the line sprite"

    def create_glyph(self, label: str, delta: Vector2) -> LineGlyph:
        length = delta.magnitude

        # create the glyph space
        space = AffineSpace()

        # create a sprite, lying horizontally, centered on origin
        sprite = Sprite.rectangle(
            space,
            Rectangle(
                x=-length/2,
                y=-self.line_width/2,
                width=length,
                height=self.line_width
            ),
            fill_color=self.color,
            dpi=self.dpi
        )

        # create the two points
        start_point = ScenePoint(
            point=Point(-length/2, 0),
            space=space
        )
        end_point = ScenePoint(
            point=Point(length/2, 0),
            space=space
        )

        # put it all together into a line glyph
        return LineGlyph(
            space=space,
            region=Glyph.build_region_from_sprites_alpha_channel(
                label=label,
                sprites=[sprite]
            ),
            sprites=[sprite],
            start_point=start_point,
            end_point=end_point
        )
