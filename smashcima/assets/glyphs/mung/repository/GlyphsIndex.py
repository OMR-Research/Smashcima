from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Tuple

from smashcima.scene import Glyph

from .PackedGlyph import PackedGlyph


@dataclass
class GlyphsIndex:
    """Holds glyphs, optimized for fast randomized sampling by class and style"""

    glyphs_by_label: \
        Dict[str, List[PackedGlyph]] = field(default_factory=dict)
    "Contains all glyphs grouped by glyph label"

    glyphs_by_label_and_style: \
        Dict[Tuple[str, str], List[PackedGlyph]] = field(default_factory=dict)
    "Contains all glyphs grouped by glyph label and style identifier"

    @staticmethod
    def build(glyphs: List[Glyph]) -> "GlyphsIndex":
        return GlyphsIndex.build_from_packed(
            [PackedGlyph.pack_glyph(glyph) for glyph in glyphs]
        )
    
    @staticmethod
    def build_from_packed(packed_glyphs: List[PackedGlyph]) -> "GlyphsIndex":
        glyphs_by_label: Dict[str, List[PackedGlyph]] = {}
        glyphs_by_label_and_style: Dict[Tuple[str, str], List[PackedGlyph]] = {}
        
        for packed_glyph in packed_glyphs:
            key1 = packed_glyph.label
            glyphs_by_label.setdefault(key1, [])
            glyphs_by_label[key1].append(packed_glyph)

            key2 = (packed_glyph.label, packed_glyph.mung_style)
            glyphs_by_label_and_style.setdefault(key2, [])
            glyphs_by_label_and_style[key2].append(packed_glyph)

        return GlyphsIndex(
            glyphs_by_label=glyphs_by_label,
            glyphs_by_label_and_style=glyphs_by_label_and_style
        )
    
    def iter_packed_glyphs(self) -> Iterator[PackedGlyph]:
        """Returns an iterator over all contained packed glyphs"""
        for glyphs in self.glyphs_by_label.values():
            yield from glyphs
