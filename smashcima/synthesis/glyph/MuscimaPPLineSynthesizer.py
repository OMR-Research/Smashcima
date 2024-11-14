from smashcima.scene.LineGlyph import LineGlyph
from smashcima.scene.SmashcimaLabels import SmashcimaLabels
from ..LineSynthesizer import LineSynthesizer
from smashcima.geometry.Vector2 import Vector2
from smashcima.assets.AssetRepository import AssetRepository
from smashcima.assets.glyphs.muscima_pp.MuscimaPPGlyphs import MuscimaPPGlyphs
from smashcima.assets.glyphs.muscima_pp.LineList import LineList
from smashcima.scene.SmuflLabels import SmuflLabels
from smashcima.synthesis.style.MuscimaPPStyleDomain import MuscimaPPStyleDomain
from typing import Dict
import random
import copy


_QUERY_TO_MPP_LOOKUP: Dict[str, str] = {
    SmashcimaLabels.ledgerLine.value: SmashcimaLabels.ledgerLine.value,
    SmuflLabels.stem.value: SmuflLabels.stem.value,
    SmashcimaLabels.beam.value: SmashcimaLabels.beam.value,
    SmashcimaLabels.beamHook.value: SmashcimaLabels.beamHook.value,
}


class MuscimaPPLineSynthesizer(LineSynthesizer):
    """
    Synthesizes line glyphs by sampling from the MUSCIMA++ dataset
    """
    def __init__(
        self,
        assets: AssetRepository,
        mpp_style_domain: MuscimaPPStyleDomain,
        rng: random.Random
    ):
        bundle = assets.resolve_bundle(MuscimaPPGlyphs)
        self.symbol_repository = bundle.load_symbol_repository()
        "The symbol repository used for synthesis"

        self.mpp_style_domain = mpp_style_domain
        "Dictates which MUSCIMA++ writer to use for synthesis"
        
        self.rng = rng
        "RNG used for randomization"
    
    def create_glyph(self, label: str, delta: Vector2) -> LineGlyph:
        # translate glyph class
        if label not in _QUERY_TO_MPP_LOOKUP:
            raise Exception("Unsupported glyph label: " + label)
        mpp_label = _QUERY_TO_MPP_LOOKUP[label]

        # select the proper glyph list
        glyphs = self.symbol_repository.glyphs_by_class_and_writer.get(
            (mpp_label, self.mpp_style_domain.current_writer)
        ) or self.symbol_repository.glyphs_by_class.get(mpp_label)
        assert isinstance(glyphs, LineList), \
            f"Got line glyphs without index for {mpp_label}"

        if glyphs is None or len(glyphs) == 0:
            raise Exception(
                f"The glyph class {label} is not present in " + \
                "the symbol repository"
            )

        # pick a random glyph from the list and copy it
        glyph = copy.deepcopy(
            glyphs.pick_line(delta.magnitude, self.rng)
        )

        # ensure the label
        glyph.label = label

        return glyph

