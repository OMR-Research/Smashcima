from smashcima.assets.AssetRepository import AssetRepository
from smashcima.assets.textures.MzkPaperPatches import MzkPaperPatches, Patch
from smashcima.assets.glyphs.muscima_pp.MuscimaPPGlyphs import MuscimaPPGlyphs
from pathlib import Path
from dataclasses import dataclass
from typing import List, Literal, Union
from .utils import REPO_FOLDER, random_name, img_smashcima2gradio
import numpy as np


ASSET_REPO = AssetRepository.default()


#################
# Writer Styles #
#################

mpp_glyphs = ASSET_REPO.resolve_bundle(MuscimaPPGlyphs)
mpp_symbol_repo = mpp_glyphs.load_symbol_repository()
WRITERS = list(sorted(mpp_symbol_repo.get_all_styles()))

####

@dataclass
class GlyphStyle:
    title: str
    dataset: Union[Literal["muscima_pp"], Literal["omni_omr"]]
    style: str


GLYPH_STYLES: List[GlyphStyle] = [
    GlyphStyle(
        title="w" + str(writer_number).zfill(2),
        dataset="muscima_pp",
        style=str(writer_number)
    )
    for writer_number in sorted(
        map(int, mpp_symbol_repo.get_all_styles())
    )
]


######################
# Background Samples #
######################


@dataclass
class BackgroundSample:
    patch: Patch
    title: str
    gradio_image: np.ndarray


paper_patches_bundle = ASSET_REPO.resolve_bundle(MzkPaperPatches)

BACKGROUND_SAMPLES: List[BackgroundSample] = [
    BackgroundSample(
        patch=patch,
        title=random_name(),
        gradio_image=img_smashcima2gradio(
            paper_patches_bundle.load_bitmap_for_patch(patch)
        )
    )
    for patch in paper_patches_bundle.load_patch_index()
]


########################
# Input MusicXML Files #
########################

MXL_FILES: List[Path] = [
    REPO_FOLDER / "testing" / "lc6247269.musicxml", # TODO: move into the demos folder
    REPO_FOLDER / "jupyter" / "layout_synthesis" / "notehead_placement.musicxml",
    REPO_FOLDER / "jupyter" / "layout_synthesis" / "rests.musicxml",
    REPO_FOLDER / "jupyter" / "layout_synthesis" / "stems.musicxml",
    REPO_FOLDER / "jupyter" / "layout_synthesis" / "beams.musicxml",
    REPO_FOLDER / "jupyter" / "layout_synthesis" / "flags.musicxml",
    REPO_FOLDER / "jupyter" / "layout_synthesis" / "leger_lines.musicxml",
    REPO_FOLDER / "jupyter" / "layout_synthesis" / "duration_dots.musicxml",
    REPO_FOLDER / "jupyter" / "layout_synthesis" / "accidentals.musicxml",
]
