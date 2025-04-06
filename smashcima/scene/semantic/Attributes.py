from dataclasses import dataclass
from typing import Dict, Optional
from .Clef import Clef
from .TimeSignature import TimeSignature
from .KeySignature import KeySignature
from .AttributesChange import AttributesChange


@dataclass
class Attributes:
    """A state in all the attribute values valid for a given event.
    It's basicaly a running aggregation of AttributesChange objects."""

    staff_count: int
    "Number of staves (in this part)"

    clefs: Dict[int, Clef]
    """Clefs by staff number (staff number starts from 1 for the top staff).
    There's a value for each staff."""

    keys: Dict[int, KeySignature]
    """Key signatures by staff number (staff number starts from 1 for the top
    staff). There's a value for each staff."""

    time_signature: Optional[TimeSignature]
    """Time signature, None means unspecified time signature, i.e. measures
    have unknown or variable number of beats"""

    def __post_init__(self):
        assert self.staff_count >= 1, "There must be a positive number of staves"
        assert set(self.clefs.keys()) == set(range(1, self.staff_count+1)), \
            "There is not one clef exactly for each staff"
        assert set(self.keys.keys()) == set(range(1, self.staff_count+1)), \
            "There is not one key signature exactly for each staff"
    
    def apply_change(self, change: AttributesChange) -> "Attributes":
        """Applies a change and returns the resulting attributes"""
        clefs = dict()
        clefs.update(self.clefs)
        clefs.update(change.clefs)

        keys = dict()
        keys.update(self.keys)
        keys.update(change.keys)

        return Attributes(
            staff_count=self.staff_count,
            clefs=clefs,
            keys=keys,
            time_signature=change.time_signature or self.time_signature
        )
    
    @staticmethod
    def from_first_change(
        staff_count: int,
        change: AttributesChange
    ) -> "Attributes":
        """Creates the attributes object from the very first change object"""
        return Attributes(
            staff_count=staff_count,
            clefs=change.clefs, # verified in post-init
            keys=change.keys, # verified in post-init
            time_signature=change.time_signature
        )
