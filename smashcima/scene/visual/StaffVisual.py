from dataclasses import dataclass, field
from typing import List

from ..AffineSpace import AffineSpace
from ..SceneObject import SceneObject
from ..Sprite import Sprite
from .StaffCoordinateSystem import StaffCoordinateSystem


@dataclass
class StaffVisual(SceneObject):
    """Represents the visual stafflines for a staff on the page"""

    width: float
    "Width (in millimeters) of these stafflines"

    staff_coordinate_system: StaffCoordinateSystem
    "Coordinate system that maps from pitch-time space to 2D position"

    space: AffineSpace = field(default_factory=AffineSpace)
    "The affine space that contains all glyphs on these stafflines"

    sprites: List[Sprite] = field(default_factory=list)
    "Sprites that together make up the stafflines visually"
