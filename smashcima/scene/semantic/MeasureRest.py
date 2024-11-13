from dataclasses import dataclass
from .RestSemantic import RestSemantic
from .TypeDuration import TypeDuration
from .Pitch import Pitch
from fractions import Fraction
from typing import Optional


@dataclass
class MeasureRest(RestSemantic):
    def __init__(
        self,
        fractional_duration: Fraction,
        display_pitch: Optional[Pitch]
    ):
        """Constructs the measure rest, given the fractional duration of
        the whole measure (the number of beats)"""
        super().__init__(
            type_duration=TypeDuration.whole,
            augmentation_dots=0,
            fractional_duration=fractional_duration,
            display_pitch=display_pitch
        )
