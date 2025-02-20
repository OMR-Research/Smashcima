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

    # ...

    def extract_c_clefs(self):
        for node in self.iterate_nodes(["cClef"]):
            self.emit_glyph_from_mung_node(
                node=node,
                glyph_label=SmuflLabels.cClef.value,
                sprite_origin=Point(0.5, 0.5)
            )
