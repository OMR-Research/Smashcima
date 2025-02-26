from ..mung.repository.MungSymbolRepository import MungSymbolRepository
from smashcima.scene import Glyph, LineGlyph
from ...AssetBundle import AssetBundle
from ...datasets.MuscimaPP import MuscimaPP
from smashcima.exporting.DebugGlyphRenderer import DebugGlyphRenderer
from .MppPage import MppPage
from smashcima.scene.SmuflLabels import SmuflLabels
from smashcima.scene.SmashcimaLabels import SmashcimaLabels
from .get_symbols import \
    get_full_noteheads, \
    get_empty_noteheads, \
    get_normal_barlines, \
    get_whole_rests, \
    get_half_rests, \
    get_quarter_rests, \
    get_eighth_rests, \
    get_sixteenth_rests, \
    get_g_clefs, \
    get_f_clefs, \
    get_c_clefs, \
    get_stems, \
    get_beams, \
    get_beam_hooks, \
    get_leger_lines, \
    get_flags, \
    get_duration_dots, \
    get_staccato_dots, \
    get_accidentals, \
    get_brackets_and_braces, \
    get_time_marks
from .MppGlyphMetadata import MppGlyphMetadata
from pathlib import Path
import pickle
from tqdm import tqdm
import shutil
import cv2
from typing import Any, List, Optional


# Re-install asset bunle during development by running:
# .venv/bin/python3 -m smashcima.assets.glyphs.muscima_pp --debug

class MuscimaPPGlyphs(AssetBundle):
    def __post_init__(self) -> None:
        self._symbol_repository_cache: Optional[MungSymbolRepository] = None

        self.muscima_pp = self.dependency_resolver.resolve_bundle(MuscimaPP)

    @property
    def symbol_repository_path(self) -> Path:
        return self.bundle_directory / "symbol_repository.pkl"
    
    def install(self) -> None:
        """Extracts data from the MUSCIMA++ dataset and bundles it up
        in the symbol repository in a pickle file."""
        document_paths = list(
            self.muscima_pp.cropobjects_directory.glob("CVC-MUSCIMA_*-ideal.xml")
        )

        items: List[Any] = []

        # go through all the MUSCIMA++ XML files
        for document_path in tqdm(document_paths):
            page = MppPage.load(document_path)

            # and extract glyphs
            items += get_full_noteheads(page)
            items += get_empty_noteheads(page)
            items += get_normal_barlines(page)
            items += get_whole_rests(page)
            items += get_half_rests(page)
            items += get_quarter_rests(page)
            items += get_eighth_rests(page)
            items += get_sixteenth_rests(page)
            items += get_g_clefs(page)
            items += get_f_clefs(page)
            items += get_c_clefs(page)
            items += get_stems(page)
            items += get_beams(page)
            items += get_beam_hooks(page)
            items += get_leger_lines(page)
            items += get_duration_dots(page)
            items += get_staccato_dots(page)
            items += get_accidentals(page)
            items += get_brackets_and_braces(page)
            items += get_time_marks(page)
            # (flags must come after stems)
            glyphs_8th_flag, glyphs_16th_flag = get_flags(page)
            items += glyphs_8th_flag
            items += glyphs_16th_flag

            # TODO: and extract distributions

        # build the repository
        repository = MungSymbolRepository.build_from_items(items)

        # dump the repository into a pickle file
        with open(self.symbol_repository_path, "wb") as file:
            pickle.dump(repository, file)
            print("Writing...", self.symbol_repository_path)
    
    def load_symbol_repository(self) -> MungSymbolRepository:
        """Loads the symbol repository from its pickle file"""
        if self._symbol_repository_cache is None:
            with open(self.symbol_repository_path, "rb") as file:
                repository = pickle.load(file)
            assert isinstance(repository, MungSymbolRepository)
            self._symbol_repository_cache = repository

        return self._symbol_repository_cache
    
    def build_debug_folder(self):
        """Creates a debug folder in the bundle folder, where it dumps
        all the extracted glyphs for visual inspection."""
        repository = self.load_symbol_repository()
        
        debug_folder = self.bundle_directory / "debug"
        shutil.rmtree(debug_folder, ignore_errors=True)
        debug_folder.mkdir()

        def _iter_label_pgs():
            for label, pgs in repository.glyphs_index.glyphs_by_label.items():
                yield label, pgs
            for label, pgls in repository.line_glyphs_index.glyphs_by_label.items():
                yield label, pgls.lines

        # glyphs
        glyph_renderer = DebugGlyphRenderer()
        for label, packed_glyphs in _iter_label_pgs():
            glyphs_folder = debug_folder / label.replace(":", "-")
            glyphs_folder.mkdir()

            print(label, "...")
            for packed_glyph in tqdm(packed_glyphs):
                glyph = packed_glyph.unpack()
                meta = MppGlyphMetadata.of_glyph(glyph)
                cv2.imwrite(
                    str(glyphs_folder / (meta.mpp_crop_object_uid + ".png")),
                    glyph_renderer.render(glyph)
                )
