from dataclasses import dataclass
from typing import Optional
from .Durable import Durable
from .Pitch import Pitch
from .AccidentalValue import AccidentalValue


@dataclass
class Note(Durable):
    pitch: Pitch
    "Musical pitch of the note"

    accidental_value: Optional[AccidentalValue]
    "What accidental is attached to the note"
