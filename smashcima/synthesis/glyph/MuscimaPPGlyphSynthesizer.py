from typing import Set, Dict
from ..GlyphSynthesizer import GlyphSynthesizer
from smashcima.scene.Glyph import Glyph
from smashcima.assets.AssetRepository import AssetRepository
from smashcima.assets.glyphs.muscima_pp.MuscimaPPGlyphs import MuscimaPPGlyphs
from ...scene.SmuflLabels import SmuflLabels
from smashcima.synthesis.style.MuscimaPPStyleDomain import MuscimaPPStyleDomain
import random


_QUERY_TO_MPP_LOOKUP: Dict[str, str] = {
    # barlines
    SmuflLabels.barlineSingle.value: SmuflLabels.barlineSingle.value,

    # clefs    (clefs ignore the normal/small distinction)
    SmuflLabels.gClef.value: SmuflLabels.gClef.value,
    SmuflLabels.gClefSmall.value: SmuflLabels.gClef.value,
    SmuflLabels.fClef.value: SmuflLabels.fClef.value,
    SmuflLabels.fClefSmall.value: SmuflLabels.fClef.value,
    SmuflLabels.cClef.value: SmuflLabels.cClef.value,
    SmuflLabels.cClefSmall.value: SmuflLabels.cClef.value,

    # noteheads
    SmuflLabels.noteheadWhole.value: SmuflLabels.noteheadWhole.value,
    SmuflLabels.noteheadHalf.value: SmuflLabels.noteheadWhole.value,
    SmuflLabels.noteheadBlack.value: SmuflLabels.noteheadBlack.value,

    # augmentation dot
    SmuflLabels.augmentationDot.value:SmuflLabels.augmentationDot.value,

    # flags
    SmuflLabels.flag8thUp.value: SmuflLabels.flag8thUp.value,
    SmuflLabels.flag8thDown.value: SmuflLabels.flag8thDown.value,
    SmuflLabels.flag16thUp.value: SmuflLabels.flag16thUp.value,
    SmuflLabels.flag16thDown.value: SmuflLabels.flag16thDown.value,

    # accidentals
    SmuflLabels.accidentalFlat.value: SmuflLabels.accidentalFlat.value,
    SmuflLabels.accidentalNatural.value: SmuflLabels.accidentalNatural.value,
    SmuflLabels.accidentalSharp.value: SmuflLabels.accidentalSharp.value,

    # rests
    SmuflLabels.restWhole.value: SmuflLabels.restWhole.value,
    SmuflLabels.restHalf.value: SmuflLabels.restHalf.value,
    SmuflLabels.restQuarter.value: SmuflLabels.restQuarter.value,
    SmuflLabels.rest8th.value: SmuflLabels.rest8th.value,
    SmuflLabels.rest16th.value: SmuflLabels.rest16th.value,
}


class MuscimaPPGlyphSynthesizer(GlyphSynthesizer):
    """Synthesizes glyphs by sampling from the MUSCIMA++ dataset"""
    
    def __init__(
        self,
        assets: AssetRepository,
        mpp_style_domain: MuscimaPPStyleDomain,
        rng: random.Random,
    ):
        bundle = assets.resolve_bundle(MuscimaPPGlyphs)
        self.symbol_repository = bundle.load_symbol_repository()
        "The symbol repository used for synthesis"

        self.mpp_style_domain = mpp_style_domain
        "Dictates which MUSCIMA++ writer to use for synthesis"
        
        self.rng = rng
        "RNG used for randomization"

    def supports_label(self, label: str) -> bool:
        return label in _QUERY_TO_MPP_LOOKUP

    def create_glyph(self, label: str) -> Glyph:
        # pick a glyph from the symbol repository
        if label in _QUERY_TO_MPP_LOOKUP:
            glyph = self.pick(_QUERY_TO_MPP_LOOKUP[label])
        else:
            raise Exception("Unsupported glyph label: " + label)

        # adjust its glyph class to match what the user wants
        # (because the mapping dictionary is not really 1:1)
        glyph.label = label

        return glyph
    
    def pick(self, label: str) -> Glyph:
        """Picks a random glyph from the symbol repository according to the
        current writer"""
        # get the list of glyphs to choose from
        # (if writer is missing this class, fall back on all writers)
        packed_glyphs = self.symbol_repository.glyphs_by_class_and_writer.get(
            (label, self.mpp_style_domain.current_writer)
        ) or self.symbol_repository.glyphs_by_class.get(label)

        if packed_glyphs is None or len(packed_glyphs) == 0:
            raise Exception(
                f"The glyph class {label} is not present in " + \
                "the symbol repository"
            )
        
        # pick a random glyph from the list
        packed_glyph = self.rng.choice(packed_glyphs)
        
        # deserialization here makes sure we create a new instance
        return packed_glyph.unpack()
