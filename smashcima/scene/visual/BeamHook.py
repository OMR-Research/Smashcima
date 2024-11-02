from .LineGlyph import LineGlyph
from .BeamCoordinateSystem import BeamCoordinateSystem
from ..semantic.Chord import Chord
from ..semantic.BeamedGroup import BeamedGroup
from dataclasses import dataclass
from ..semantic.BeamValue import BeamValue


@dataclass
class BeamHook(LineGlyph):
    """One hook glyph in a beamed group (visually)"""

    beamed_group: BeamedGroup = None
    "The beamed group this beam belongs to"

    chord: Chord = None
    """The chord in whose stem the hook is placed"""

    beam_number: int = 1
    """Which beam is this beam (1 being the 8th notes beam).
    Uses the MusicXML numbering."""

    hook_type: BeamValue = None
    """Either forward hook or backward hook. Any other value is invalid."""

    def detach(self):
        """Unlink the glyph from the scene"""
        super().detach()
        self.beamed_group = None
        self.chord = None
