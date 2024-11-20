from dataclasses import dataclass
from .Measure import Measure
from .ScoreEvent import ScoreEvent
from .StaffSemantic import StaffSemantic
from typing import List, Iterator, Tuple


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
    
    def measure_for_staff(self, staff_index: int) -> Measure:
        """Returns the part measure that contains the given staff index"""
        assert staff_index < sum(len(m.staves) for m in self.measures), \
            "Staff index is larger than the number of staves in the score"
        mi = 0
        skipped_staves = 0
        while skipped_staves + len(self.measures[mi].staves) < staff_index:
            mi += 1
            skipped_staves += len(self.measures[mi].staves)
        return self.measures[mi]

    def iterate_staves_with_measures(
        self
    ) -> Iterator[Tuple[StaffSemantic, Measure]]:
        """Iterates over semantic staves and their measures in the score"""
        for measure in self.measures:
            for staff in measure.staves:
                yield (staff, measure)
