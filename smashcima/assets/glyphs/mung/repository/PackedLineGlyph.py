import pickle

from smashcima.scene import LineGlyph

from ..MungGlyphMetadata import MungGlyphMetadata
from .PackedGlyph import PackedGlyph


class PackedLineGlyph(PackedGlyph):
    """Like PackedGlyph, but packs a line glyph instead"""
    def __init__(
        self,
        line_length: float,
        label: str,
        mung_style: str,
        data: bytes
    ):
        super().__init__(
            label=label,
            mung_style=mung_style,
            data=data
        )

        self.line_length = line_length
        """If a line glyph, stores its length for sampling lookups"""

    @staticmethod
    def pack_line_glyph(glyph: LineGlyph) -> "PackedLineGlyph":
        assert isinstance(glyph, LineGlyph)
        return PackedLineGlyph(
            line_length=glyph.line_length,
            label=glyph.label,
            mung_style=MungGlyphMetadata.of_glyph(glyph).mung_style,
            data=pickle.dumps(glyph)
        )
    
    def unpack(self) -> LineGlyph:
        g = super().unpack()
        assert isinstance(g, LineGlyph)
        return g
