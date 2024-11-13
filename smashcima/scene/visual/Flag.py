from ..Glyph import Glyph
from ..SceneObject import SceneObject
from .Stem import Stem
from dataclasses import dataclass


@dataclass
class Flag(SceneObject):
    """Glyph of a flag with flag-related properties"""

    glyph: Glyph
    "Glyph of the flag"

    stem: Stem
    "The stem that the flag is attached to"

    def detach(self):
        """Unlink the glyph from the scene"""
        self.glyph.detach()
        self.stem = None
