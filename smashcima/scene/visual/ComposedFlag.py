from .ComposedGlyph import ComposedGlyph
from .Flag import Flag
from .Stem import Stem
from dataclasses import dataclass


@dataclass
class ComposedFlag(Flag, ComposedGlyph):
    """Glyph of a flag which is actually a composite of isolated flag strokes"""
    pass
