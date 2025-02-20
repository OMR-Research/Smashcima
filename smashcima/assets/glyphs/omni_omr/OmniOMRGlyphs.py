import pickle
import shutil
from pathlib import Path
from typing import Any, List, Optional

import cv2
from tqdm import tqdm

from smashcima.exporting.DebugGlyphRenderer import DebugGlyphRenderer

from ...AssetBundle import AssetBundle
from ...datasets.OmniOMRProto import OmniOMRProto
from ..mung.MungGlyphMetadata import MungGlyphMetadata
from ..mung.repository.MungSymbolRepository import MungSymbolRepository
from .get_symbols import get_full_noteheads
from .OmniOMRDocument import OmniOMRDocument


class OmniOMRGlyphs(AssetBundle):
    def __post_init__(self) -> None:
        self._symbol_repository_cache: Optional[MungSymbolRepository] = None

        self.omni_omr_proto = self.dependency_resolver.resolve_bundle(
            OmniOMRProto
        )
    
    @property
    def symbol_repository_path(self) -> Path:
        return self.bundle_directory / "symbol_repository.pkl"

    def install(self) -> None:
        """Extracts data from the OmniOMR dataset and bundles it up
        in the symbol repository in a pickle file."""
        document_paths = list(
            self.omni_omr_proto.mung_directory.glob("*.xml")
        )

        items: List[Any] = []

        # go through all the MUSCIMA++ XML files
        for document_path in tqdm(document_paths):
            document = OmniOMRDocument.load(document_path)

            items += get_full_noteheads(document)
            # ...
            
            # TODO: DEBUG
            print("DEBUG! BREAKING AFTER THE FIRST DOCUMENT")
            break

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
                meta = MungGlyphMetadata.of_glyph(glyph)
                cv2.imwrite(
                    str(glyphs_folder / (meta.mung_document + "_" + str(meta.mung_node_id) + ".png")),
                    glyph_renderer.render(glyph)
                )

