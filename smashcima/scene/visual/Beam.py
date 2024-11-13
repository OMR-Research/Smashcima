from ..SceneObject import SceneObject
from ..LineGlyph import LineGlyph
from ..semantic.Chord import Chord
from ..semantic.BeamedGroup import BeamedGroup
from dataclasses import dataclass
from typing import List


@dataclass
class Beam(SceneObject):
    """One beam (one line) in a beamed group (visually)"""

    glyph: LineGlyph
    "The glyph of the beam"

    beamed_group: BeamedGroup
    "The beamed group this beam belongs to"

    chords: List[Chord]
    """List of chords that are tied together by this beam
    (in chronological order)"""

    beam_number: int
    """Which beam is this beam (1 being the 8th notes beam).
    Uses the MusicXML numbering."""

    def detach(self):
        """Unlink the glyph from the scene"""
        self.glyph.detach()
        self.beamed_group = None
        self.chords = []
