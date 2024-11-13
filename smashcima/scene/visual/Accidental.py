from ..Glyph import Glyph
from .Notehead import Notehead
from dataclasses import dataclass
from typing import List, Union, Optional


@dataclass
class Accidental(Glyph):
    """Glyph of an accidental"""

    notehead: Notehead = None
    """The notehead that the accidental belongs to."""

    def detach(self):
        """Unlink the glyph from the scene"""
        super().detach()
        self.notehead = None
