from ..LineGlyph import LineGlyph
from ..SceneObject import SceneObject
from ..semantic.Chord import Chord
from dataclasses import dataclass
from typing import Optional
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

    @classmethod
    def of_chord(cls, chord: Chord):
        return cls.of(chord, lambda s: s.chord)

    @classmethod
    def of_chord_or_none(cls, chord: Optional[Chord]):
        return cls.of_or_none(chord, lambda s: s.chord)
