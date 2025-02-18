from dataclasses import dataclass
from typing import Optional

from smashcima.scene import Glyph, SceneObject


@dataclass
class MungGlyphMetadata(SceneObject):
    """Metadata information object for a glyph from a MuNG file"""

    glyph: Glyph
    """The glyph that this metadata refers to"""
    
    mung_style: str
    """Style identifier for the glyph (writer number, book ID, etc.)"""

    mung_document: str
    """Document identifier for the glyph (XML file name without extension)"""

    mung_node_id: int
    """Integer ID of the MuNG node within its document"""

    def __post_init__(self):
        assert self.glyph is not None
        assert self.mung_style is not None
        assert self.mung_document is not None
    
    @classmethod
    def of_glyph(cls, glyph: Glyph):
        return cls.of(glyph, lambda m: m.glyph)

    @classmethod
    def of_glyph_or_none(cls, glyph: Optional[Glyph]):
        return cls.of_or_none(glyph, lambda m: m.glyph)
