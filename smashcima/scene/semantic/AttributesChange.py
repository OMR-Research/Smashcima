from dataclasses import dataclass, field
from typing import Optional, Dict
from .Clef import Clef
from .TimeSignature import TimeSignature
from .KeySignature import KeySignature


@dataclass
class AttributesChange:
    """A change in the part attributes (clefs, keys), attached to an event"""
    # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/attributes/

    clefs: Dict[int, Clef] = field(default_factory=dict)
    """Clefs by staff number (staff number starts from 1 for the top staff).
    If a clef does not change for the given staff, it is not present here."""

    keys: Dict[int, KeySignature] = field(default_factory=dict)
    """Key signatures by staff number (staff number starts from 1 for the top
    staff). If a key does not change for the given staff, it is not present."""

    time_signature: Optional[TimeSignature] = None
    """Time signature, None means unspecified time signature, i.e. measures
    have unknown or variable number of beats"""
