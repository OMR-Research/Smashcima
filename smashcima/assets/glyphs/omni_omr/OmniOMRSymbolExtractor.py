from mung.node import Node

from smashcima.scene import Glyph

from ..mung.extraction.ExtractedBag import ExtractedBag
from ..mung.extraction.MungDocument import MungDocument
from ..mung.extraction.MungSymbolExtractor import MungSymbolExtractor
from .OmniOMRGlyphMetadata import OmniOMRGlyphMetadata


class OmniOMRSymbolExtractor(MungSymbolExtractor):
    def __init__(self, document: MungDocument, bag: ExtractedBag) -> None:
        super().__init__(document, bag)

        # extract metadata
        parts = self.document.path.stem.split("_")
        assert len(parts) == 2
        self.mzk_book_uuid: str = parts[0]
        self.mzk_page_uuid: str = parts[1]

    def stamp_glyph(self, glyph: Glyph, node: Node):
        OmniOMRGlyphMetadata.stamp_glyph(
            glyph=glyph,
            node=node,
            mzk_book_uuid=self.mzk_book_uuid,
            mzk_page_uuid=self.mzk_page_uuid
        )
