from dataclasses import dataclass
from typing import List, Optional

from ..Glyph import Glyph
from ..SceneObject import SceneObject
from ..semantic import Clef, Note
from .NoteheadSide import NoteheadSide
from .StaffVisual import StaffVisual


@dataclass
class Notehead(SceneObject):
    """A notehead in a music score"""

    glyph: Glyph
    "The visual glyph of the notehead"

    notes: List[Note]
    "List of notes being represented by this notehead (typically just one)"

    clef: Clef
    "What clef applies to the note (notehead)"

    staff: StaffVisual
    "What stafflines is the notehead placed onto"

    pitch_position: int
    "Pitch position of the notehead on the stafflines"

    up_stem_attachment_side: Optional[NoteheadSide] = NoteheadSide.right
    """On what side of the notehead should an up-pointing stem be attached.
    Notehead placing algorithm can modify this, e.g. in a dense
    chord where noteheads have to be from both sides of the stem.
    None means there should not ever be such a stem attached."""

    down_stem_attachment_side: Optional[NoteheadSide] = NoteheadSide.left
    """On what side of the notehead should a down-pointing stem be attached.
    Notehead placing algorithm can modify this, e.g. in a dense
    chord where noteheads have to be from both sides of the stem.
    None means there should not ever be such a stem attached."""

    def detach(self):
        """Unlink the notehead from the scene"""
        self.glyph.detach()
        self.notes = []

    @classmethod
    def of_note(cls, note: Note):
        return cls.of(note, lambda n: n.notes)
