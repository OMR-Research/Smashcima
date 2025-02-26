from smashcima.geometry.units import px_to_mm
from .MungDocument import MungDocument
from .ExtractedBag import ExtractedBag
from smashcima.geometry import Point
from smashcima.scene.SmuflLabels import SmuflLabels

from .BaseSymbolExtractor import BaseSymbolExtractor


class MungSymbolExtractor(BaseSymbolExtractor):
    """Defines methods for extracting symbols from one MuNG document.
    Still needs to be overriden to define the metadata stamping logic."""

    def __init__(self, document: MungDocument, bag: ExtractedBag):
        super().__init__(document=document, bag=bag)

        self.TALL_BARLINE_THRESHOLD_MM = 16.0
        """When do we start considering barlines to be 'tall' (i.e. multi-staff).
        The average size of a staff (the 5 lines) is cca 8 millimeters."""
    
    def extract_full_noteheads(self):
        for node in self.iterate_nodes(["noteheadFull"],
            lambda n: not self.graph.has_children(n, ["ledgerLine"])
        ):
            self.emit_glyph_from_mung_node(
                node=node,
                glyph_label=SmuflLabels.noteheadBlack.value,
                sprite_origin=Point(0.5, 0.5)
            )
    
    def extract_empty_noteheads(self):
        for node in self.iterate_nodes(["noteheadHalf"],
            lambda n: not self.graph.has_children(n, ["ledgerLine"])
        ):
            self.emit_glyph_from_mung_node(
                node=node,
                glyph_label=SmuflLabels.noteheadWhole.value,
                sprite_origin=Point(0.5, 0.5)
            )

    def extract_whole_rests(self):
        for node in self.iterate_nodes(["restWhole"]):
            self.emit_glyph_on_staffline(
                node=node,
                glyph_label=SmuflLabels.restWhole.value,
                staffline_index_from_top=1 # 2nd line
            )

    def extract_half_rests(self):
        for node in self.iterate_nodes(["restHalf"]):
            self.emit_glyph_on_staffline(
                node=node,
                glyph_label=SmuflLabels.restHalf.value,
                staffline_index_from_top=2 # middle line
            )

    def extract_quarter_rests(self):
        for node in self.iterate_nodes(["restQuarter"]):
            self.emit_glyph_on_staffline(
                node=node,
                glyph_label=SmuflLabels.restQuarter.value,
                staffline_index_from_top=2 # middle line
            )
    
    def extract_eighth_rests(self):
        for node in self.iterate_nodes(["rest8th"]):
            self.emit_glyph_on_staffline(
                node=node,
                glyph_label=SmuflLabels.rest8th.value,
                staffline_index_from_top=2 # middle line
            )
    
    def extract_sixteenth_rests(self):
        for node in self.iterate_nodes(["rest16th"]):
            self.emit_glyph_on_staffline(
                node=node,
                glyph_label=SmuflLabels.rest16th.value,
                staffline_index_from_top=2 # middle line
            )

    def extract_normal_barlines(self):
        # TODO: barlines should be line glyphs with vertical position to
        # the edge stafflines recorded in a distribution (I guess)
        for node in self.iterate_nodes(["barline"],
            lambda n: px_to_mm(n.height, dpi=self.document.dpi) \
                < self.TALL_BARLINE_THRESHOLD_MM
        ):
            self.emit_glyph_from_mung_node(
                node=node,
                glyph_label=SmuflLabels.barlineSingle.value,
                sprite_origin=Point(0.5, 0.5)
            )

    def extract_g_clefs(self):
        # TODO: non-standard clefs need to know which staffline to pick!
        for node in self.iterate_nodes(["gClef"]):
            self.emit_glyph_on_staffline(
                node=node,
                glyph_label=SmuflLabels.gClef.value,
                staffline_index_from_top=3 # second lowest line
            )
    
    def extract_f_clefs(self):
        # TODO: non-standard clefs need to know which staffline to pick!
        for node in self.iterate_nodes(["fClef"]):
            self.emit_glyph_on_staffline(
                node=node,
                glyph_label=SmuflLabels.fClef.value,
                staffline_index_from_top=1 # second highest line
            )

    def extract_c_clefs(self):
        # TODO: non-standard clefs need to know which staffline to pick!
        # TODO: c-clef origin should also be picked by the staffline
        for node in self.iterate_nodes(["cClef"]):
            self.emit_glyph_from_mung_node(
                node=node,
                glyph_label=SmuflLabels.cClef.value,
                sprite_origin=Point(0.5, 0.5)
            )
    
    # ...

    def extract_duration_dots(self):
        for node in self.iterate_nodes(["augmentationDot"]):
            self.emit_glyph_from_mung_node(
                node=node,
                glyph_label=SmuflLabels.augmentationDot.value,
                sprite_origin=Point(0.5, 0.5)
            )
    
    def extract_staccato_dots(self):
        # TODO: staccato is annotated as an accent???
        # TODO: all accents are - need to be disambiguated
        for node in self.iterate_nodes(["articulationAccent"]):
            self.emit_glyph_from_mung_node(
                node=node,
                glyph_label=SmuflLabels.articStaccatoBelow.value,
                sprite_origin=Point(0.5, 0.5)
            )
