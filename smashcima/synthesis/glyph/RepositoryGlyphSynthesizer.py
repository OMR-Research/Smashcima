import random
from abc import ABCMeta
from typing import Optional

from smashcima.assets.glyphs.mung.repository.MungSymbolRepository import \
    MungSymbolRepository
from smashcima.scene.Glyph import Glyph
from smashcima.synthesis.style.RepositoryStyleDomain import \
    RepositoryStyleDomain

from ..GlyphSynthesizer import GlyphSynthesizer


class RepositoryGlyphSynthesizer(GlyphSynthesizer, metaclass=ABCMeta):
    """Base class for glyph synthesizer that samples a symbol repository."""
    def __init__(
        self,
        symbol_repository: MungSymbolRepository,
        style_domain: RepositoryStyleDomain,
        rng: random.Random
    ):
        self.symbol_repository = symbol_repository
        """The symbol repository used for synthesis"""

        self.all_repository_labels = symbol_repository.get_all_glyph_labels()
        """Set of all labels that the repository contains"""

        self.style_domain = style_domain
        "Dictates which style to use for synthesis"
        
        self.rng = rng
        "RNG used for randomization"

        self.fallback_synthesizer: Optional[GlyphSynthesizer] = None
        """Syntehsizer to be used if this synthesizer does not support
        the required glyph class. Can be set after the instance is created."""

    def supports_label(self, label: str) -> bool:
        # check the repository
        if label in self.all_repository_labels:
            return True
        
        # else fallback
        if self.fallback_synthesizer is not None:
            return self.fallback_synthesizer.supports_label(label)

        # else we don't support
        return False

    def create_glyph(self, label: str) -> Glyph:
        # pick a glyph from the symbol repository
        if label in self.all_repository_labels:
            return self.pick(label)
        
        # else fallback
        if self.fallback_synthesizer is not None:
            return self.fallback_synthesizer.create_glyph(label)
        
        # else fail
        raise Exception("Unsupported glyph label: " + label)
    
    def pick(self, label: str) -> Glyph:
        """Picks a random glyph from the symbol repository according to the
        current style"""
        # get the list of glyphs to choose from
        # (if style is missing for this label, fall back on all styles)
        glyphs_index = self.symbol_repository.glyphs_index
        packed_glyphs = glyphs_index.glyphs_by_label_and_style.get(
            (label, self.style_domain.current_style)
        ) or glyphs_index.glyphs_by_label.get(label)
        
        if packed_glyphs is None or len(packed_glyphs) == 0:
            raise Exception(
                f"The glyph class {label} is not present in " + \
                "the symbol repository"
            )
        
        # pick a random glyph from the list
        packed_glyph = self.rng.choice(packed_glyphs)
        
        # deserialization here makes sure we create a new instance
        glyph = packed_glyph.unpack()
    
        # ensure that the user gets the glyph class they desire
        assert glyph.label == label, \
            "Pulled a glyph of different class than advertised by the index"
        
        return glyph