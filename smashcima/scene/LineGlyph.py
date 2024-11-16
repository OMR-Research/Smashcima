from dataclasses import dataclass
from typing import List

from .Glyph import Glyph
from .ScenePoint import ScenePoint
from .Sprite import Sprite


@dataclass
class LineGlyph(Glyph):
    """Line glyph is a glyph that represents a line segment and as such is
    defined by two point (start and end) placed in the glyph space."""
    
    start_point: ScenePoint
    """Start point of the line, must be set during construction of the glyph.
    Coordinates are relative to the glyph space."""

    end_point: ScenePoint
    """End point of the line, must be set during construction of the glyph.
    Coordinates are relative to the glyph space."""

    @property
    def line_length(self) -> float:
        """Length of the line glyph"""
        return (
            self.end_point.point.vector - self.start_point.point.vector
        ).magnitude

    def place_debug_overlay(self) -> List[Sprite]:
        overlay = super().place_debug_overlay()

        # [red -> blue] is the [start -> end] points
        overlay.append(
            self.start_point.place_debug_overlay(color=(0, 0, 255, 128))
        )
        overlay.append(
            self.end_point.place_debug_overlay(color=(255, 0, 0, 128))
        )

        return overlay
