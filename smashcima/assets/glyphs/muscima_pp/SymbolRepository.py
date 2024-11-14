from typing import List, Dict, Tuple, Set
from smashcima.scene.Glyph import Glyph
from .MppGlyphMetadata import MppGlyphMetadata
from .LineList import LineList


class SymbolRepository:
    """
    Extracted glyphs from MUSCIMA++ so that they can be sampled
    by the synthesizer
    """
    def __init__(self) -> None:
        self.all_glyphs: List[Glyph] = []
        "Contains all glyphs in the repository in one big list"

        self.all_writers: Set[int] = set()
        "Contains all writer numbers that can be sampled from this repository"

        self.glyphs_by_class: Dict[str, List[Glyph]] = {}
        "Contains all glyphs grouped by glyph class"

        self.glyphs_by_class_and_writer: Dict[Tuple[str, int], List[Glyph]] = {}
        "Contains all glyphs grouped by glyph class and MPP writer number"

    def add_glyphs(self, glyphs: List[Glyph]):
        for glyph in glyphs:
            self.add_glyph(glyph)

    def add_glyph(self, glyph: Glyph):
        metadata = MppGlyphMetadata.of_glyph(glyph)
        assert metadata is not None, "Glyph must have MPP metadata attached"

        self.all_glyphs.append(glyph)

        self.all_writers.add(metadata.mpp_writer)

        key1 = glyph.label
        self.glyphs_by_class.setdefault(key1, [])
        self.glyphs_by_class[key1].append(glyph)

        key2 = (glyph.label, metadata.mpp_writer)
        self.glyphs_by_class_and_writer.setdefault(key2, [])
        self.glyphs_by_class_and_writer[key2].append(glyph)
    
    def remove_writer(self, writer: int):
        """Removes a given writer from the repository completely.
        Can be used to remove testing set when performing synthesis."""
        self.all_glyphs = list(filter(
            lambda g: MppGlyphMetadata.of_glyph(g).mpp_writer == writer,
            self.all_glyphs
        ))
        self.all_writers.remove(writer)
        for key1 in self.glyphs_by_class.keys():
            self.glyphs_by_class[key1] = list(filter(
                lambda g: MppGlyphMetadata.of_glyph(g).mpp_writer == writer,
                self.glyphs_by_class[key1]
            ))
        for key2 in self.glyphs_by_class_and_writer.keys():
            self.glyphs_by_class_and_writer[key2] = list(filter(
                lambda g: MppGlyphMetadata.of_glyph(g).mpp_writer == writer,
                self.glyphs_by_class_and_writer[key2]
            ))

    def index_lines(self, labels: List[str]):
        """Build line lookup index for each lines collection"""
        for label in labels:
            if label in self.glyphs_by_class:
                self.glyphs_by_class[label] = \
                    LineList(self.glyphs_by_class[label])

            for writer in self.all_writers:                
                if (label, writer) in self.glyphs_by_class_and_writer:
                    self.glyphs_by_class_and_writer[label, writer] = \
                        LineList(self.glyphs_by_class_and_writer[label, writer])
