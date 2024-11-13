from ..LineGlyph import LineGlyph
from ..SceneObject import SceneObject
from ..semantic.Chord import Chord
from dataclasses import dataclass
from typing import Optional
from smashcima.nameof_via_dummy import nameof_via_dummy
from ..ScenePoint import ScenePoint


@dataclass
class Stem(SceneObject):
    """Stem (visual line) belonging to a chord"""
    
    glyph: LineGlyph
    "The glyph of the line"

    chord: Chord
    """The chord containing the notes that this stem is for. Can be None
    only during construction, otherwise must be set."""

    @property
    def base(self) -> ScenePoint:
        """Base of the stem, in glyph space coordinates"""
        return self.glyph.start_point

    @property
    def tip(self) -> ScenePoint:
        """Tip of the stem, in glyph space coordinates"""
        return self.glyph.end_point
    
    def detach(self):
        """Unlink the glyph from the scene"""
        self.glyph.detach()
        self.chord = None

    @staticmethod
    def of_chord(
        chord: Chord,
        fail_if_none=False
    ) -> Optional["Stem"] | "Stem":
        return chord.get_inlinked(
            Stem,
            nameof_via_dummy(Stem, lambda s: s.chord),
            at_most_one=True,
            fail_if_none=fail_if_none
        )
