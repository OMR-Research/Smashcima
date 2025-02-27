import random
from abc import ABCMeta
from typing import Optional

from smashcima.assets.glyphs.mung.repository.MungSymbolRepository import \
    MungSymbolRepository
from smashcima.geometry.Vector2 import Vector2
from smashcima.scene.LineGlyph import LineGlyph
from smashcima.synthesis.style.RepositoryStyleDomain import \
    RepositoryStyleDomain

from ..LineSynthesizer import LineSynthesizer


class RepositoryLineSynthesizer(LineSynthesizer, metaclass=ABCMeta):
    """Base class for line synthesizer that samples a symbol repository."""
    def __init__(
        self,
        symbol_repository: MungSymbolRepository,
        style_domain: RepositoryStyleDomain,
        rng: random.Random
    ):
        self.symbol_repository = symbol_repository
        """The symbol repository used for synthesis"""

        self.all_repository_labels = symbol_repository.get_all_line_glyph_labels()
        """Set of all labels that the repository contains"""

        self.style_domain = style_domain
        "Dictates which style to use for synthesis"
        
        self.rng = rng
        "RNG used for randomization"

        self.fallback_synthesizer: Optional[LineSynthesizer] = None
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
    
    def create_glyph(self, label: str, delta: Vector2) -> LineGlyph:
        # pick a glyph from the symbol repository
        if label in self.all_repository_labels:
            return self.pick(label, delta)
        
        # else fallback
        if self.fallback_synthesizer is not None:
            return self.fallback_synthesizer.create_glyph(label, delta)
        
        # else fail
        raise Exception("Unsupported line glyph label: " + label)
    
    def pick(self, label: str, delta: Vector2) -> LineGlyph:
        """Picks a random glyph from the symbol repository according to the
        current style"""
        # select the proper glyph list
        line_glyphs_index = self.symbol_repository.line_glyphs_index
        packed_glyphs = line_glyphs_index.glyphs_by_label_and_style.get(
            (label, self.style_domain.current_style)
        ) or line_glyphs_index.glyphs_by_label.get(label)

        if packed_glyphs is None or len(packed_glyphs.lines) == 0:
            raise Exception(
                f"The glyph class {label} is not present in " + \
                "the symbol repository"
            )

        # pick a random glyph from the list
        packed_glyph = packed_glyphs.pick_line(delta.magnitude, self.rng)

        # deserialization makes sure we create a new instance here
        glyph = packed_glyph.unpack()

        # ensure that we get a line and not just a plain glyph
        assert isinstance(glyph, LineGlyph), \
            "The unpacked glyph is not a LineGlyph"

        # ensure that the user gets the glyph class they desire
        assert glyph.label == label, \
            "Pulled a line glyph of different class than advertised by the index"

        return glyph
