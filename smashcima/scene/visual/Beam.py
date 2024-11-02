from .LineGlyph import LineGlyph
from ..semantic.Chord import Chord
from ..semantic.BeamedGroup import BeamedGroup
from .BeamCoordinateSystem import BeamCoordinateSystem
from dataclasses import dataclass, field
from smashcima.nameof_via_dummy import nameof_via_dummy
from typing import List


@dataclass
class Beam(LineGlyph):
    """One beam (one line) in a beamed group (visually)"""

    beamed_group: BeamedGroup = None
    "The beamed group this beam belongs to"

    chords: List[Chord] = field(default_factory=list)
    """List of chords that are tied together by this beam
    (in chronological order)"""

    beam_number: int = 1
    """Which beam is this beam (1 being the 8th notes beam).
    Uses the MusicXML numbering."""

    def detach(self):
        """Unlink the glyph from the scene"""
        super().detach()
        self.beamed_group = None
        self.chords = []
