from abc import ABC, abstractmethod
from typing import Callable, Iterable, Iterator, Optional

import cv2
import numpy as np
from mung.node import Node

from smashcima.geometry import Point
from smashcima.scene import AffineSpace, Glyph, LineGlyph, ScenePoint, Sprite

from .ExtractedBag import ExtractedBag
from .get_line_endpoints import get_line_endpoints
from .mung_mask_to_smashcima_sprite_bitmap import \
    mung_mask_to_smashcima_sprite_bitmap
from .MungDocument import MungDocument
from .PointCloud import END_POINT, ORIGIN_POINT, START_POINT, PointCloud


class BaseSymbolExtractor(ABC):
    """Provides the scaffolding for a symbol extractor,
    but leaves the extraction logic up to the inheritor."""
    
    def __init__(self, document: MungDocument, bag: ExtractedBag):
        self.document = document
        """The document we are extracting the symbols from"""

        self.graph = document.graph
        """The music notation graph from the mung library"""

        self.point_cloud = PointCloud()
        """All extracted points in the page"""

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
    
    def emit_origin_point(
        self,
        node: Node,
        point: Point
    ):
        """Sets the origin point for the given node at the given position.
        
        :param node: The node for which to emit the point.
        :param point: The origin point in the 0-1 relative percentage
            coordinates.
        """
        self.point_cloud[node][ORIGIN_POINT] = point
    
    def emit_origin_point_on_staffline(
        self,
        node: Node,
        staffline_index_from_top: int,
        horizontal_relative_position: float = 0.5
    ):
        """Sets the origin point for the given node to align with the
        given staffline.
        
        :param node: The node for which to emit the point.
        :param staffline_index_from_top: Zero-based index of the staffline,
            going from the top-most staffline.
        :param horizontal_relative_position: The value for the X coordinate
            of the origin point, in the 0-1 relative percentage coordinates.
        """
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
        origin_point = Point(horizontal_relative_position, origin_y)

        # emit
        self.emit_origin_point(node, origin_point)
    
    def emit_line_points(
        self,
        node: Node,
        direction: str
    ) -> bool:
        """Extracts endpoints from a line-like mung node.
        
        :param direction: Unicode arrow specifying the direction in which
            to detect the line and orient start-end points. One of: ←↑→↓
        :returns: True on success, false on failure.
        """
        assert len(direction) == 1 and (direction in "←↑→↓")
        
        # horizontal_line:
        # Whether to detect line endpoints horizontally or vertically.
        #
        # in_increasing_direction:
        # Whether the lower coordinate endpoint should be considered as the
        # start point (when true) or the higher coordinate one (when false).
        horizontal_line, in_increasing_direction = {
            "←": (True, False),
            "↑": (False, False),
            "→": (True, True),
            "↓": (False, True)
        }[direction]

        blurred_mask = cv2.medianBlur(node.mask, 5) # smooth out (5x5 window)
        points = get_line_endpoints(blurred_mask) # in local pixel space
        points.sort(
            key=lambda p: p.x if horizontal_line else p.y,
            reverse=not in_increasing_direction
        )

        # skip the symbol if we did not detect any points
        if len(points) < 2:
            return False
        
        start_point = points[0]
        end_point = points[-1]

        # transform both points into the percentage 0-1 relative space
        # and insert them into the point cloud
        self.point_cloud[node][START_POINT] = Point(
            start_point.x / node.width, start_point.y / node.height
        )
        self.point_cloud[node][END_POINT] = Point(
            end_point.x / node.width, end_point.y / node.height
        )
        self.point_cloud[node][ORIGIN_POINT] = Point(0.5, 0.5)
        return True
    
    def sprite_bitmap_from_mung_node(self, node: Node) -> np.ndarray:
        """This method creates the smashcima sprite bitmap for the given
        mung node. The default behaviour is to convert the mask to black
        on transparent. You can override this method to alter this logic."""
        return mung_mask_to_smashcima_sprite_bitmap(node.mask)

    def emit_glyph_from_mung_node(
        self,
        node: Node,
        glyph_label: str
    ):
        """Creates a glyph from a MuNG node by treating the mask as the only
        sprite the glyph consists of and interpreting the mask as
        black-on-transparent.
        
        :param node: The node used for the construction of the glyph.
        :param glyph_label: What classification label should the glyph have.
        """
        
        # create the glyph instance
        space = AffineSpace()
        sprite = Sprite(
            space=space,
            bitmap=self.sprite_bitmap_from_mung_node(node),
            bitmap_origin=self.point_cloud[node][ORIGIN_POINT],
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
    
    def emit_line_glyph_from_mung_node(
        self,
        node: Node,
        glyph_label: str
    ):
        """Creates a line glyph from mung node, positions the sprite origin
        to the middle of the mask and detects the two line endpoints.
        """
        # skip nodes for which points have not been extracted
        if node not in self.point_cloud:
            return
        
        points = self.point_cloud[node]

        # construct the glyph
        space = AffineSpace()
        sprite = Sprite(
            space=space,
            bitmap=self.sprite_bitmap_from_mung_node(node),
            bitmap_origin=points.get_in_relative_ratio(ORIGIN_POINT),
            dpi=self.document.dpi
        )
        start_point = ScenePoint(
            point=sprite.get_pixels_to_origin_space_transform().apply_to(
                points.get_in_relative_pixels(START_POINT)
            ),
            space=space
        )
        end_point = ScenePoint(
            point=sprite.get_pixels_to_origin_space_transform().apply_to(
                points.get_in_relative_pixels(END_POINT)
            ),
            space=space
        )
        line_glyph = LineGlyph(
            space=space,
            region=Glyph.build_region_from_sprites_alpha_channel(
                label=glyph_label,
                sprites=[sprite]
            ),
            sprites=[sprite],
            start_point=start_point,
            end_point=end_point
        )

        # stamp on the metadata
        self.stamp_glyph(line_glyph, node)

        # and add to the bag
        self.bag.add_line_glyph(line_glyph)

    ################################
    # Aggregate Extraction Methods #
    ################################
    
    def extract_all_symbols(self):
        """Executes extraction logic for all implemented symbols"""
        # preparatory step that builds the point cloud
        # (extracts points for individual mung nodes)
        self.extract_all_points()

        # collects up delta vectors from the point cloud
        self.extract_all_deltas()

        # build the smashcima glyphs to be used in synthesis
        # (this utilizes points from the point cloud)
        self.extract_all_glyphs()
    
    def extract_all_points(self):
        """Goes through mung nodes and extracts origins and other points.
        Prepares the content of the point cloud used in later stages."""
        self.extract_points_noteheadBlack()
        self.extract_points_noteheadHalf()
        self.extract_points_restWhole()
        self.extract_points_restHalf()
        self.extract_points_restQuarter()
        self.extract_points_rest8th()
        self.extract_points_rest16th()
        self.extract_points_barlineSingle()
        self.extract_points_gClef()
        self.extract_points_fClef()
        self.extract_points_cClef()
        self.extract_points_stem()
        self.extract_points_beam()
        self.extract_points_beamHook()
        self.extract_points_legerLine()
        # ...flags
        self.extract_points_augmentationDot()
        self.extract_points_articStaccatoBelow()
        self.extract_points_accidentalSharp()
        self.extract_points_accidentalFlat()
        self.extract_points_accidentalNatural()
        self.extract_points_accidentalDoubleSharp()
        self.extract_points_accidentalDoubleFlat()
        self.extract_points_bracket()
        self.extract_points_brace()
        self.extract_points_timeSig()

    def extract_all_deltas(self):
        """Computes delta vectors from the point cloud. Delta vectors are
        relative jumps in millimeters between related glyphs, e.g. notehead
        to its accidental or stem length+direction."""
        pass # TODO: implement delta sampling

    def extract_all_glyphs(self):
        """Extracts all glyph classes and constructs their smashcima instances"""
        self.extract_glyphs_noteheadBlack()
        self.extract_glyphs_noteheadWhole()
        self.extract_glyphs_restWhole()
        self.extract_glyphs_restHalf()
        self.extract_glyphs_restQuarter()
        self.extract_glyphs_rest8th()
        self.extract_glyphs_rest16th()
        self.extract_glyphs_barlineSingle()
        self.extract_glyphs_gClef()
        self.extract_glyphs_fClef()
        self.extract_glyphs_cClef()
        self.extract_glyphs_stem()
        self.extract_glyphs_beam()
        self.extract_glyphs_beamHook()
        self.extract_glyphs_legerLine()
        # ... flags
        self.extract_glyphs_augmentationDot()
        self.extract_glyphs_articStaccatoBelow()
        self.extract_glyphs_accidentalSharp()
        self.extract_glyphs_accidentalFlat()
        self.extract_glyphs_accidentalNatural()
        self.extract_glyphs_accidentalDoubleSharp()
        self.extract_glyphs_accidentalDoubleFlat()
        self.extract_glyphs_bracket()
        self.extract_glyphs_brace()
        self.extract_glyphs_timeSig()

    ############################
    # Point Extraction Methods #
    ############################

    @abstractmethod
    def extract_points_noteheadBlack(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_noteheadHalf(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_restWhole(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_restHalf(self):
        raise NotImplementedError

    @abstractmethod
    def extract_points_restQuarter(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_rest8th(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_rest16th(self):
        raise NotImplementedError

    @abstractmethod
    def extract_points_barlineSingle(self):
        raise NotImplementedError

    @abstractmethod
    def extract_points_gClef(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_fClef(self):
        raise NotImplementedError

    @abstractmethod
    def extract_points_cClef(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_stem(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_beam(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_beamHook(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_legerLine(self):
        raise NotImplementedError
    
    # ...

    @abstractmethod
    def extract_points_augmentationDot(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_articStaccatoBelow(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_accidentalSharp(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_accidentalFlat(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_accidentalNatural(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_accidentalDoubleSharp(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_accidentalDoubleFlat(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_bracket(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_brace(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_points_timeSig(self):
        raise NotImplementedError

    ############################
    # Delta Extraction Methods #
    ############################

    # ...
    
    ############################
    # Glyph Extraction Methods #
    ############################

    @abstractmethod
    def extract_glyphs_noteheadBlack(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_glyphs_noteheadWhole(self):
        raise NotImplementedError

    @abstractmethod
    def extract_glyphs_restWhole(self):
        raise NotImplementedError

    @abstractmethod
    def extract_glyphs_restHalf(self):
        raise NotImplementedError

    @abstractmethod
    def extract_glyphs_restQuarter(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_glyphs_rest8th(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_glyphs_rest16th(self):
        raise NotImplementedError

    @abstractmethod
    def extract_glyphs_barlineSingle(self):
        raise NotImplementedError

    @abstractmethod
    def extract_glyphs_gClef(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_glyphs_fClef(self):
        raise NotImplementedError

    @abstractmethod
    def extract_glyphs_cClef(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_glyphs_stem(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_glyphs_beam(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_glyphs_beamHook(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_glyphs_legerLine(self):
        raise NotImplementedError

    # ...

    @abstractmethod
    def extract_glyphs_augmentationDot(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_glyphs_articStaccatoBelow(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_glyphs_accidentalSharp(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_glyphs_accidentalFlat(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_glyphs_accidentalNatural(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_glyphs_accidentalDoubleSharp(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_glyphs_accidentalDoubleFlat(self):
        raise NotImplementedError

    @abstractmethod
    def extract_glyphs_bracket(self):
        raise NotImplementedError
    
    @abstractmethod
    def extract_glyphs_brace(self):
        raise NotImplementedError

    @abstractmethod
    def extract_glyphs_timeSig(self):
        raise NotImplementedError
