import random

from smashcima.assets.AssetRepository import AssetRepository
from smashcima.assets.glyphs.omni_omr.OmniOMRGlyphs import OmniOMRGlyphs
from smashcima.scene.Glyph import Glyph
from smashcima.synthesis.style.OmniOMRStyleDomain import OmniOMRStyleDomain

from .MuscimaPPGlyphSynthesizer import LABEL_MAP as MPP_LABEL_MAP
from .RepositoryGlyphSynthesizer import RepositoryGlyphSynthesizer

LABEL_MAP = {
    **MPP_LABEL_MAP
}


class OmniOMRGlyphSynthesizer(RepositoryGlyphSynthesizer):
    """Synthesizes glyphs by sampling from the OmniOMR dataset"""
    
    def __init__(
        self,
        assets: AssetRepository,
        style_domain: OmniOMRStyleDomain,
        rng: random.Random
    ):
        symbol_repository = (
            assets.resolve_bundle(OmniOMRGlyphs).load_symbol_repository()
        )

        super().__init__(
            symbol_repository=symbol_repository,
            style_domain=style_domain,
            rng=rng
        )

    def supports_label(self, label: str) -> bool:
        return label in LABEL_MAP
    
    def create_glyph(self, label: str) -> Glyph:
        glyph = super().create_glyph(LABEL_MAP[label])

        # adjust glyph label to match what the user wants
        # (because the label map is not 1:1)
        glyph.label = label

        return glyph
