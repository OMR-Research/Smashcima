import csv
import pickle
import shutil
import traceback
from pathlib import Path
from typing import Dict, Optional

import cv2
from tqdm import tqdm

from smashcima.exporting.DebugGlyphRenderer import DebugGlyphRenderer

from ...AssetBundle import AssetBundle
from ...datasets.OmniOMRProto import OmniOMRProto
from ..mung.extraction.ExtractedBag import ExtractedBag
from ..mung.extraction.MungDocument import MungDocument
from ..mung.MungGlyphMetadata import MungGlyphMetadata
from ..mung.repository.MungSymbolRepository import MungSymbolRepository
from ..mung.utils.link_nodes_to_staves import \
    link_nodes_to_staves
from ..mung.utils.link_stafflines_to_staves import link_stafflines_to_staves
from .OmniOMRSymbolExtractor import OmniOMRSymbolExtractor


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

        dpi_lookup = self._load_dpi_lookup()

        # collects extracted symbols
        bag = ExtractedBag()

        # go through all the MuNG XML files
        for document_path in tqdm(document_paths):
            print(document_path.stem, "@", dpi_lookup[document_path.stem])
            document = MungDocument.load(
                document_path,
                dpi=dpi_lookup[document_path.stem]
            )

            try:
                # correct for things missing in the proto dataset
                link_stafflines_to_staves(document.graph)
                link_nodes_to_staves(document.graph)

                extractor = OmniOMRSymbolExtractor(document=document, bag=bag)
                extractor.extract_all_symbols()
            except Exception as e:
                print(traceback.format_exc())

        # build the repository
        repository = bag.build_symbol_repository()

        # dump the repository into a pickle file
        with open(self.symbol_repository_path, "wb") as file:
            pickle.dump(repository, file)
            print("Writing...", self.symbol_repository_path)
    
    def _load_dpi_lookup(self) -> Dict[str, float]:
        """Loads the 'dpi_values.csv' lookup table"""
        index_path = Path(__file__).parent / "dpi_values.csv"

        lookup: Dict[str, float] = {}

        with open(index_path, "r") as f:
            reader = csv.reader(f, delimiter=",", quotechar='"')

            # header
            assert next(reader) == [
                "document", "dpi"
            ]

            # records
            for record in reader:
                lookup[record[0]] = float(record[1])
        
        return lookup
    
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

