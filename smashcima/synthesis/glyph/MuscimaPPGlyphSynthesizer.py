import random
from typing import Dict

from smashcima.assets.AssetRepository import AssetRepository
from smashcima.assets.glyphs.muscima_pp.MuscimaPPGlyphs import MuscimaPPGlyphs
from smashcima.scene.Glyph import Glyph
from smashcima.synthesis.style.MuscimaPPStyleDomain import MuscimaPPStyleDomain

from ...scene.SmuflLabels import SmuflLabels
from .RepositoryGlyphSynthesizer import RepositoryGlyphSynthesizer

LABEL_MAP: Dict[str, str] = {
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


class MuscimaPPGlyphSynthesizer(RepositoryGlyphSynthesizer):
    """Synthesizes glyphs by sampling from the MUSCIMA++ dataset"""
    
    def __init__(
        self,
        assets: AssetRepository,
        style_domain: MuscimaPPStyleDomain,
        rng: random.Random
    ):
        symbol_repository = (
            assets.resolve_bundle(MuscimaPPGlyphs).load_symbol_repository()
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
