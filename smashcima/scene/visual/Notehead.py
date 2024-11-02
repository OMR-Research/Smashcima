from dataclasses import dataclass, field
from typing import List, Optional
from ..semantic.Note import Note
from ..semantic.Clef import Clef
from .Stafflines import Stafflines
from .Glyph import Glyph
from .NoteheadSide import NoteheadSide
from smashcima.nameof_via_dummy import nameof_via_dummy


@dataclass
class Notehead(Glyph):
    """Glyph of a notehead, contains links specific to a notehead glyph"""

    notes: List[Note] = field(default_factory=list)
    "List of notes being represented by this notehead (typically just one)"

    clef: Clef = None
    "What clef applies to the note (notehead)"

    stafflines: Stafflines = None
    "What stafflines is the notehead placed onto"

    pitch_position: int = None
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
        """Unlink the glyph from the scene"""
        super().detach()
        self.notes = []

    @staticmethod
    def of_note(
        note: Note,
        fail_if_none=False
    ) -> Optional["Notehead"] | "Notehead":
        return note.get_inlinked(
            Notehead,
            nameof_via_dummy(Notehead, lambda n: n.notes),
            at_most_one=True,
            fail_if_none=fail_if_none
        )
