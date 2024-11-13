from dataclasses import dataclass, field
from ..SceneObject import SceneObject
from ..ViewBox import ViewBox
from ..AffineSpace import AffineSpace
from .StaffVisual import StaffVisual
from typing import List


@dataclass
class Page(SceneObject):
    """Represents the visual page of music that is synthesized.
    There may be more than one page in a scene."""

    space: AffineSpace
    "Affine space of the page, origin in the top left corner."

    view_box: ViewBox
    "The view box that renders the page, in the global space"

    staves: List[StaffVisual] = field(default_factory=list)
    "Stafflines on the page, sorted top to bottom"
