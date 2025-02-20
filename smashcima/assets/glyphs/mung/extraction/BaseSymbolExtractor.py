from abc import ABC, abstractmethod
from typing import Callable, Iterable, Iterator, List, Optional

from mung.node import Node

from smashcima.geometry import Point
from smashcima.scene import AffineSpace, Glyph, LineGlyph, Sprite

from .ExtractedBag import ExtractedBag
from .mung_mask_to_smashcima_sprite_bitmap import \
    mung_mask_to_smashcima_sprite_bitmap
from .MungDocument import MungDocument


class BaseSymbolExtractor(ABC):
    """Provides the scaffolding for a symbol extractor,
    but leaves the extraction logic up to the inheritor."""
    
    def __init__(self, document: MungDocument, bag: ExtractedBag):
        self.document = document
        """The document we are extracting the symbols from"""

        self.graph = document.graph
        """The music notation graph from the mung library"""

        self.bag = bag
        """Collection of extracted symbols we will add to"""
    
    @abstractmethod
    def stamp_glyph(self, glyph: Glyph, node: Node):
        """Stamps an extracted glyph with metadata about its origin"""
        raise NotImplementedError
    
    ##############################
    # Utility Extraction Methods #
    ##############################
    
    def iterate_nodes(
        self,
        class_filter: Iterable[str],
        predicate: Optional[Callable[[Node], bool]] = None
    ) -> Iterator[Node]:
        """Lets you iterate a subset of MuNG nodes based on their class and
        optional filtration predicate"""
        if predicate is None:
            predicate = lambda n: True
        
        for node in self.graph.vertices:
            if (node.class_name in class_filter) and predicate(node):
                yield node

    def emit_glyph_from_mung_node(
        self,
        node: Node,
        glyph_label: str,
        sprite_origin: Point
    ):
        """Creates a glyph from a MuNG node by treating the mask as the only
        sprite the glyph consists of and interpreting the mask as
        black-on-transparent."""

        # create the glyph instance
        space = AffineSpace()
        sprite = Sprite(
            space=space,
            bitmap=mung_mask_to_smashcima_sprite_bitmap(node.mask),
            bitmap_origin=sprite_origin,
            dpi=self.document.dpi
        )
        glyph = Glyph(
            space=space,
            region=Glyph.build_region_from_sprites_alpha_channel(
                label=glyph_label,
                sprites=[sprite]
            ),
            sprites=[sprite]
        )

        # stamp on the metadata
        self.stamp_glyph(glyph, node)

        # and add to the bag
        self.bag.add_glyph(glyph)

    ###############################
    # Specific Extraction Methods #
    ###############################
    
    def extract_all_symbols(self):
        """Executes extraction logic for all implemented symbols"""
        self.extract_full_noteheads()
        self.extract_empty_noteheads()
        # ...
        self.extract_c_clefs()
        # ...

    @abstractmethod
    def extract_full_noteheads(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_empty_noteheads(self):
        raise NotImplementedError

    # ...

    @abstractmethod
    def extract_c_clefs(self):
        raise NotImplementedError
