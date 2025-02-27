from .RepositoryStyleDomain import RepositoryStyleDomain
from smashcima.assets.AssetRepository import AssetRepository
from smashcima.assets.glyphs.muscima_pp.MuscimaPPGlyphs import MuscimaPPGlyphs
import random
from typing import List


class MuscimaPPStyleDomain(RepositoryStyleDomain):
    """This style domain represents the set of 50 writers of the MUSCIMA++
    dataset. When sampled, one of these writers is chosen."""

    def __init__(self, assets: AssetRepository, rng: random.Random):
        symbol_repository = (
            assets.resolve_bundle(MuscimaPPGlyphs).load_symbol_repository()
        )

        super().__init__(
            symbol_repository=symbol_repository,
            rng=rng
        )
    
    @property
    def all_writers(self) -> List[int]:
        """The domain of all MPP writers (their numbers)"""
        return [int(style) for style in self.all_styles]
    
    @property
    def current_writer(self) -> int:
        """The writer number to be used for the currently synthesized sample"""
        return int(self.current_style)
