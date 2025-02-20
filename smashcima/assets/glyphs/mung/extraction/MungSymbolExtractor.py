from smashcima.geometry import Point
from smashcima.scene.SmuflLabels import SmuflLabels

from .BaseSymbolExtractor import BaseSymbolExtractor


class MungSymbolExtractor(BaseSymbolExtractor):
    """Defines methods for extracting symbols from one MuNG document.
    Still needs to be overriden to define the metadata stamping logic."""
    
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

    # ...

    def extract_c_clefs(self):
        for node in self.iterate_nodes(["cClef"]):
            self.emit_glyph_from_mung_node(
                node=node,
                glyph_label=SmuflLabels.cClef.value,
                sprite_origin=Point(0.5, 0.5)
            )
