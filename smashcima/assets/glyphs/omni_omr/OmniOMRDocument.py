from pathlib import Path
from typing import List

from mung.io import read_nodes_from_file
from mung.node import Node

from smashcima.scene import Glyph

from ..mung.MungDocument import MungDocument
from .OmniOMRGlyphMetadata import OmniOMRGlyphMetadata


class OmniOMRDocument(MungDocument):
    def __init__(
        self,
        path: Path,
        nodes: List[Node]
    ):
        super().__init__(
            path=path,
            nodes=nodes
        )

    @staticmethod
    def load(path: Path) -> "MungDocument":
        nodes: List[Node] = read_nodes_from_file(str(path))
        return OmniOMRDocument(
            path=path,
            nodes=nodes
        )

    def stamp_glyph(self, glyph: Glyph, node: Node):
        parts = self.path.stem.split("_")
        assert len(parts) == 2
        mzk_book_uuid = parts[0]
        mzk_page_uuid = parts[1]
        
        OmniOMRGlyphMetadata.stamp_glyph(
            glyph=glyph,
            node=node,
            mzk_book_uuid=mzk_book_uuid,
            mzk_page_uuid=mzk_page_uuid
        )
