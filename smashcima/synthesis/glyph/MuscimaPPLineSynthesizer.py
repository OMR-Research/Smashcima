from smashcima.scene.SmashcimaLabels import SmashcimaLabels
from .NaiveLineSynthesizer import NaiveLineSynthesizer, T
from smashcima.geometry.Vector2 import Vector2
from smashcima.assets.AssetRepository import AssetRepository
from smashcima.assets.glyphs.muscima_pp.MuscimaPPGlyphs import MuscimaPPGlyphs
from smashcima.assets.glyphs.muscima_pp.LineList import LineList
from smashcima.scene.SmuflLabels import SmuflLabels
from smashcima.synthesis.style.MuscimaPPStyleDomain import MuscimaPPStyleDomain
from typing import Type, Dict
import random
import copy


_QUERY_TO_MPP_LOOKUP: Dict[str, str] = {
    SmashcimaLabels.ledgerLine.value: SmashcimaLabels.ledgerLine.value,
    SmuflLabels.stem.value: SmuflLabels.stem.value,
    SmashcimaLabels.beam.value: SmashcimaLabels.beam.value,
    SmashcimaLabels.beamHook.value: SmashcimaLabels.beamHook.value,
}


class MuscimaPPLineSynthesizer(NaiveLineSynthesizer):
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
    
    def pick(
        self,
        glyph_type: Type[T],
        glyph_class: str,
        delta: Vector2,
    ) -> T:
        # translate glyph class
        if glyph_class not in _QUERY_TO_MPP_LOOKUP:
            raise Exception("Unsupported glyph class: " + glyph_class)
        mpp_glyph_class = _QUERY_TO_MPP_LOOKUP[glyph_class]

        # select the proper glyph list
        glyphs = self.symbol_repository.glyphs_by_class_and_writer.get(
            (mpp_glyph_class, self.mpp_style_domain.current_writer)
        ) or self.symbol_repository.glyphs_by_class.get(mpp_glyph_class)
        assert isinstance(glyphs, LineList), \
            f"Got line glyphs without index for {mpp_glyph_class}"

        if glyphs is None or len(glyphs) == 0:
            raise Exception(
                f"The glyph class {glyph_class} is not present in " + \
                "the symbol repository"
            )

        # pick a random glyph from the list and copy it
        glyph = copy.deepcopy(
            glyphs.pick_line(delta.magnitude, self.rng)
        )

        assert type(glyph) is glyph_type, \
            f"Picked glyph is of different type: {type(glyph)}"
        
        # ensure the class
        glyph.glyph_class = glyph_class

        return glyph

