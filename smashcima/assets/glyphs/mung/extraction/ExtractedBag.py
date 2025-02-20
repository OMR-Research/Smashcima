from typing import List

from smashcima.scene import Glyph, LineGlyph

from ..repository.MungSymbolRepository import MungSymbolRepository


class ExtractedBag:
    """A container that collects extracted symbols from many pages."""
    
    def __init__(self) -> None:
        self.glyphs: List[Glyph] = []
        """Collects extracted glyph instances (excluding line glyphs)"""

        self.line_glyphs: List[LineGlyph] = []
        """Collects extracted line glyph instances"""
    
    def add_glyph(self, glyph: Glyph):
        """Adds a glyph instance into the bag"""
        assert isinstance(glyph, Glyph)
        assert not isinstance(glyph, LineGlyph)
        self.glyphs.append(glyph)
    
    def add_line_glyph(self, line_glyph: LineGlyph):
        """Adds a line glyph instance into the bag"""
        assert isinstance(line_glyph, LineGlyph)
        self.line_glyphs.append(line_glyph)
    
    def build_symbol_repository(self) -> MungSymbolRepository:
        """Builds a new symbol repository instance from extracted symbols"""
        return MungSymbolRepository.build_from_items(
            self.glyphs + self.line_glyphs
        )
