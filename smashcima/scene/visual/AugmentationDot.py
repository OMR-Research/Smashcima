from ..Glyph import Glyph
from ..SceneObject import SceneObject
from .Notehead import Notehead
from .RestVisual import RestVisual
from dataclasses import dataclass
from typing import List, Union


@dataclass
class AugmentationDot(SceneObject):
    """Glyph of an augmentation dot"""

    glyph: Glyph
    """The dot glyph"""

    owners: List[Union[Notehead, RestVisual]]
    """The glyph(s) that is(are) affected by this augmentation dot.
    For noteheads in dense chords, augmentation dots may be shared.
    Otherwise it's usually one-to-one"""

    augmentation_dot_index: int
    """Which dot (out of many for the owner) is this dot?
    Starting from 1, increasing 2, 3, 4."""

    pitch_position: int
    """At what pitch position should the augmentation dot be placed."""

    def detach(self):
        """Unlink the glyph from the scene"""
        self.glyph.detach()
        self.owners = []
