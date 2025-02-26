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
    
    def emit_glyph_on_staffline(
        self,
        node: Node,
        glyph_label: str,
        staffline_index_from_top: int
    ):
        """Creates a glyph from mung node and positions the sprite origin
        vertically to align with the given staffline"""
        assert staffline_index_from_top >= 0 and staffline_index_from_top < 5
        
        # get the staffline
        linked_staff_nodes = self.graph.children(node, ["staff"])
        assert len(linked_staff_nodes) > 0, \
            "There is no linked staff for the given MuNG node"
        staff_node = linked_staff_nodes[0]
        staffline_nodes = self.graph.children(staff_node, ["staffLine"])

        assert len(staffline_nodes) == 5, \
            "The linked staff does not have 5 stafflines"
        staffline_nodes.sort(key=lambda s: s.top)
        staffline_node = staffline_nodes[staffline_index_from_top]
        
        # compute origin point
        line_y = (staffline_node.top + staffline_node.bottom) // 2
        origin_y = (line_y - node.top) / node.height
        sprite_origin = Point(0.5, origin_y)

        # emit the glyph
        self.emit_glyph_from_mung_node(
            node=node,
            glyph_label=glyph_label,
            sprite_origin=sprite_origin
        )

    ###############################
    # Specific Extraction Methods #
    ###############################
    
    def extract_all_symbols(self):
        """Executes extraction logic for all implemented symbols"""
        self.extract_full_noteheads()
        self.extract_empty_noteheads()
        self.extract_whole_rests()
        self.extract_half_rests()
        self.extract_quarter_rests()
        self.extract_eighth_rests()
        self.extract_sixteenth_rests()
        self.extract_normal_barlines()
        # ...

        self.extract_c_clefs()
        # ...

    @abstractmethod
    def extract_full_noteheads(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_empty_noteheads(self):
        raise NotImplementedError

    @abstractmethod
    def extract_whole_rests(self):
        raise NotImplementedError

    @abstractmethod
    def extract_half_rests(self):
        raise NotImplementedError

    @abstractmethod
    def extract_quarter_rests(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_eighth_rests(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_sixteenth_rests(self):
        raise NotImplementedError

    @abstractmethod
    def extract_normal_barlines(self):
        raise NotImplementedError

    # ...

    @abstractmethod
    def extract_c_clefs(self):
        raise NotImplementedError
