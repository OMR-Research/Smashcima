from dataclasses import dataclass
from typing import Any, Callable, List, Set

from smashcima.scene import Glyph, LineGlyph

from .GlyphsIndex import GlyphsIndex
from .LineGlyphsIndex import LineGlyphsIndex


@dataclass
class MungSymbolRepository:
    """Encapsualtes glyphs and vectors extracted from a MuNG-based dataset.
    
    The purpose of this class is to be pickled to disk, so that it can be
    quickly loaded when glyphs need to be synthesized. It encapsualtes all
    synthesis-related data that can be extracted from a MUSCIMA++-like dataset
    (a dataset annotated with the MuNG format).
    """
    
    glyphs_index: GlyphsIndex
    """Hols all non-line glyphs"""
    
    line_glyphs_index: LineGlyphsIndex
    """Holds all line glyphs"""

    # deltas_index = None
    # """TODO: holds all delta vector distributions"""
    
    def get_all_styles(self) -> Set[str]:
        all_styles = set()
        for _, style in self.glyphs_index.glyphs_by_label_and_style.keys():
            all_styles.add(style)
        for _, style in self.line_glyphs_index.glyphs_by_label_and_style.keys():
            all_styles.add(style)
        # TODO: delta vectors styles
        return all_styles
    
    def get_all_glyph_labels(self) -> Set[str]:
        return set(
            label for label, _
            in self.glyphs_index.glyphs_by_label_and_style.keys()
        )
    
    def get_all_line_glyph_labels(self) -> Set[str]:
        return set(
            label for label, _
            in self.line_glyphs_index.glyphs_by_label_and_style.keys()
        )
    
    # TODO: delta vectors labels

    @staticmethod
    def build_from_items(items: List[Any]) -> "MungSymbolRepository":
        return MungSymbolRepository(
            glyphs_index=GlyphsIndex.build([
                i for i in items
                if isinstance(i, Glyph) and not isinstance(i, LineGlyph)
            ]),
            line_glyphs_index=LineGlyphsIndex.build([
                i for i in items
                if isinstance(i, LineGlyph)
            ])
        )

    def filter_styles(
        self,
        predicate: Callable[[str], bool]
    ) -> "MungSymbolRepository":
        """Creates a copy of the repository with elements filtered based on
        the given mung style predicate.
        
        Use this method when you want to constrain the synthesized styles,
        for example to exclude the test portion of the underlying dataset."""
        return MungSymbolRepository(
            glyphs_index=GlyphsIndex.build_from_packed([
                g for g in self.glyphs_index.iter_packed_glyphs()
                if predicate(g.mung_style)
            ]),
            line_glyphs_index=LineGlyphsIndex.build_from_packed([
                g for g in self.line_glyphs_index.iter_packed_glyphs()
                if predicate(g.mung_style)
            ])
        )
