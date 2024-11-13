from ..SceneObject import SceneObject
from ..LineGlyph import LineGlyph
from .Notehead import Notehead
from .RestGlyph import RestGlyph
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LedgerLine(SceneObject):
    """Ledger line (visual), extending the stafflines outside their range"""
    
    glyph: LineGlyph

    affected_noteheads: List[Notehead] = field(default_factory=list)
    """List of noteheads that are affected by this ledger line (so if we are
    at the top of the staff, all notes that are on or above this ledger line
    fall into this list; notes that are below this ledger line are not affected.
    The list contains only noteheads from the same onset event.)
    If this list is empty, then this ledger line affects a (whole/half) rest."""

    affected_rest: Optional[RestGlyph] = None
    """A ledger line is also needed for whole and half rests. Here, the
    placement is simpler, because there are no intermediate lines drawn,
    only the one that directly touches the rest."""

    def detach(self):
        """Unlink the glyph from the scene"""
        self.glyph.detach()
        self.affected_noteheads = None
        self.affected_rest = None
