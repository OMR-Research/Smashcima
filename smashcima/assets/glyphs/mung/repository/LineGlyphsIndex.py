from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Tuple

from smashcima.scene import LineGlyph

from .GlyphsIndex import GlyphsIndex
from .PackedLineGlyph import PackedLineGlyph
from .PackedLineList import PackedLineList


@dataclass
class LineGlyphsIndex:
    """Holds glyphs, optimized for fast randomized sampling by class and style"""
    
    glyphs_by_label: \
        Dict[str, PackedLineList] = field(default_factory=dict)
    "Contains all line glyphs grouped by glyph label"

    glyphs_by_label_and_style: \
        Dict[Tuple[str, str], PackedLineList] = field(default_factory=dict)
    "Contains all line glyphs grouped by glyph label and style identifier"

    @staticmethod
    def build(glyphs: List[LineGlyph]) -> "LineGlyphsIndex":
        return LineGlyphsIndex.build_from_packed(
            [PackedLineGlyph.pack_line_glyph(glyph) for glyph in glyphs]
        )

    @staticmethod
    def build_from_packed(
        packed_glyphs: List[PackedLineGlyph]
    ) -> "LineGlyphsIndex":
        plain_index = GlyphsIndex.build_from_packed(
            packed_glyphs # type: ignore
        )
        return LineGlyphsIndex(
            glyphs_by_label={
                key1: PackedLineList(lines) # type: ignore
                for key1, lines in plain_index.glyphs_by_label.items()
            },
            glyphs_by_label_and_style={
                key2: PackedLineList(lines) # type: ignore
                for key2, lines in plain_index.glyphs_by_label_and_style.items()
            }
        )

    def iter_packed_glyphs(self) -> Iterator[PackedLineGlyph]:
        """Returns an iterator over all contained packed glyphs"""
        for packed_line_list in self.glyphs_by_label.values():
            yield from packed_line_list.lines

