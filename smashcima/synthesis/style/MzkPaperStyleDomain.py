from .StyleDomain import StyleDomain
from smashcima.assets.AssetRepository import AssetRepository
from smashcima.assets.textures.MzkPaperPatches import MzkPaperPatches, Patch
import random
from typing import List


class MzkPaperStyleDomain(StyleDomain):
    """This style domain represents the set of paper texture patches
    that are used to synthesize the paper texture."""

    def __init__(self, assets: AssetRepository, rng: random.Random):
        bundle = assets.resolve_bundle(MzkPaperPatches)
        
        self.all_patches: List[Patch] = bundle.load_patch_index()
        "All paper texture patches available in the bundle"
        
        self.rng = rng
        "The RNG used for randomness"

        assert len(self.all_patches) > 0, "There must be at least one patch"

        # use the first patch as the default
        # (the pick_style will be called before the first sampling)
        self.current_patch: Patch = self.all_patches[0]
        "The patch to be used for the currently synthesized sample"

    def pick_style(self):
        self.current_patch = self.rng.choice(self.all_patches)
