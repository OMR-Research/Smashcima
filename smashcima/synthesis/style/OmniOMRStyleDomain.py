import random

from smashcima.assets.AssetRepository import AssetRepository
from smashcima.assets.glyphs.omni_omr.OmniOMRGlyphs import OmniOMRGlyphs

from .RepositoryStyleDomain import RepositoryStyleDomain


class OmniOMRStyleDomain(RepositoryStyleDomain):
    def __init__(self, assets: AssetRepository, rng: random.Random):
        symbol_repository = (
            assets.resolve_bundle(OmniOMRGlyphs).load_symbol_repository()
        )

        super().__init__(
            symbol_repository=symbol_repository,
            rng=rng
        )
