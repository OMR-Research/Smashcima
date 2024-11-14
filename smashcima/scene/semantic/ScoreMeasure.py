from dataclasses import dataclass
from .Measure import Measure
from .ScoreEvent import ScoreEvent
from typing import List


@dataclass
class ScoreMeasure:
    """A view of an entire score in a time-wise manner"""
    
    measures: List[Measure]
    "Part-measures ordered just like parts in the score"

    events: List[ScoreEvent]
    "Temporally-ordered musical events (sets of durables with the same onset)"

    @staticmethod
    def from_part_measures(measures: List[Measure]) -> "ScoreMeasure":
        return ScoreMeasure(
            measures=measures,
            events=ScoreEvent.merge_from_measures(measures)
        )
