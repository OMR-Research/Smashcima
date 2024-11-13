from ..SceneObject import SceneObject
from ..LineGlyph import LineGlyph
from ..semantic.Chord import Chord
from ..semantic.BeamedGroup import BeamedGroup
from dataclasses import dataclass
from ..semantic.BeamValue import BeamValue


@dataclass
class BeamHook(SceneObject):
    """One hook glyph in a beamed group (visually)"""

    glyph: LineGlyph
    "The beam hook glyph"

    beamed_group: BeamedGroup
    "The beamed group this beam belongs to"

    chord: Chord
    """The chord in whose stem the hook is placed"""

    beam_number: int
    """Which beam is this beam (1 being the 8th notes beam).
    Uses the MusicXML numbering."""

    hook_type: BeamValue
    """Either forward hook or backward hook. Any other value is invalid."""

    def detach(self):
        """Unlink the glyph from the scene"""
        self.glyph.detach()
        self.beamed_group = None
        self.chord = None
