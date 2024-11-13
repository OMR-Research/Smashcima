from dataclasses import dataclass
from .Durable import Durable
from .Pitch import Pitch
from typing import Optional


@dataclass
class RestSemantic(Durable):
    display_pitch: Optional[Pitch]
    """Display pitch controls where the rest is placed vertically.
    If none, default placement should be used. For more information
    on the positioning, see the RestGlyph class."""
