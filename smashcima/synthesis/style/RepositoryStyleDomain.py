import random
from abc import ABCMeta
from typing import List

from smashcima.assets.glyphs.mung.repository.MungSymbolRepository import \
    MungSymbolRepository

from .StyleDomain import StyleDomain


class RepositoryStyleDomain(StyleDomain, metaclass=ABCMeta):
    """This style domain represents the set of all styles present
    in the given symbol repository."""

    def __init__(
        self,
        symbol_repository: MungSymbolRepository,
        rng: random.Random
    ):
        self.all_styles: List[str] = list(sorted(
            style for style in symbol_repository.get_all_styles()
        ))
        "The domain of all repository styles"
        
        self.rng = rng
        "The RNG used for randomness"

        assert len(self.all_styles) > 0, "There must be at least one style"

        # use the first style as the default
        # (the pick_style will be called before the first sampling)
        self.current_style: str = self.all_styles[0]
        "The style to be used for the currently synthesized sample"

    def pick_style(self):
        self.current_style = self.rng.choice(self.all_styles)
