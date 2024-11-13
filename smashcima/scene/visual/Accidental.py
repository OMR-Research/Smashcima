from ..Glyph import Glyph
from ..SceneObject import SceneObject
from .Notehead import Notehead
from dataclasses import dataclass


@dataclass
class Accidental(SceneObject):
    """Glyph of an accidental"""

    glyph: Glyph
    """The glyph of the accidental"""

    notehead: Notehead
    """The notehead that the accidental belongs to."""

    def detach(self):
        """Unlink the glyph from the scene"""
        self.glyph.detach()
        self.notehead = None
