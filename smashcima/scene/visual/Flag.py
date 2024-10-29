from .Glyph import Glyph
from .Stem import Stem
from dataclasses import dataclass


@dataclass
class Flag(Glyph):
    """Glyph of a flag with flag-related properties"""

    stem: Stem = None
    "The stem that the flag is attached to"
