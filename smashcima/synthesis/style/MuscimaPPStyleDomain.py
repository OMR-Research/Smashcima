from .StyleDomain import StyleDomain
from smashcima.assets.AssetRepository import AssetRepository
from smashcima.assets.glyphs.muscima_pp.MuscimaPPGlyphs import MuscimaPPGlyphs
import random
from typing import List


class MuscimaPPStyleDomain(StyleDomain):
    """This style domain represents the set of 50 writers of the MUSCIMA++
    dataset. When sampled, one of these writers is chosen."""

    def __init__(self, assets: AssetRepository, rng: random.Random):
        bundle = assets.resolve_bundle(MuscimaPPGlyphs)
        symbol_repository = bundle.load_symbol_repository()
        
        self.all_writers: List[int] = list(sorted(
            int(style) for style in symbol_repository.get_all_styles()
        ))
        "The domain of all MPP writers (their numbers)"
        
        self.rng = rng
        "The RNG used for randomness"

        assert len(self.all_writers) > 0, "There must be at least one writer"

        # use the first writer as the default
        # (the pick_style will be called before the first sampling)
        self.current_writer: int = self.all_writers[0]
        "The writer number to be used for the currently synthesized sample"

    def pick_style(self):
        self.current_writer = self.rng.choice(self.all_writers)
