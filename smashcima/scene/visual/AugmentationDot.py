from ..Glyph import Glyph
from .Notehead import Notehead
from .RestGlyph import RestGlyph
from dataclasses import dataclass, field
from typing import List, Union


@dataclass
class AugmentationDot(Glyph):
    """Glyph of an augmentation dot"""

    owners: List[Union[Notehead | RestGlyph]] = field(default_factory=list)
    """The glyph(s) that is(are) affected by this augmentation dot.
    For noteheads in dense chords, augmentation dots may be shared.
    Otherwise it's usually one-to-one"""

    augmentation_dot_index: int = 1
    """Which dot (out of many for the owner) is this dot?
    Starting from 1, increasing 2, 3, 4."""

    pitch_position: int = None
    """At what pitch position should the augmentation dot be placed."""

    def detach(self):
        """Unlink the glyph from the scene"""
        super().detach()
        self.owners = []
