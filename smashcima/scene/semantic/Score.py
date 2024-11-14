from dataclasses import dataclass, field
from ..SceneObject import SceneObject
from typing import List, Set
from .Part import Part
from .ScoreMeasure import ScoreMeasure
from .StaffSemantic import StaffSemantic
from .Measure import Measure
from .Durable import Durable


@dataclass
class Score(SceneObject):
    """Represents a whole music score (a single MusicXML file)"""
    
    parts: List[Part]
    "List of parts that this score consists of"

    new_system_measure_indices: Set[int] = field(default_factory=set)
    "Indices of measures that should be placed on a new system (line breaks)"

    new_page_measure_indices: Set[int] = field(default_factory=set)
    "Indices of measures that should be placed on a new page (page breaks)"

    @property
    def staff_count(self) -> int:
        """How many staves does a single system have"""
        assert len(self.parts) > 0, "There are no parts in the score"
        return sum(p.staff_count for p in self.parts)
    
    @property
    def measure_count(self) -> int:
        """How many measures does the score have in total"""
        assert len(self.parts) > 0, "There are no parts in the score"
        return len(self.parts[0].measures)
    
    def first_staff_index_of_part(self, part: Part) -> int:
        """Given a part returns the staff index (zero-based) of the first staff
        in that part, relative to the system (the score, all the instruments)"""
        index = 0

        for p in self.parts:
            if p is part:
                return index
            else:
                index += p.staff_count

        raise Exception("The given part is not a part of this score.")
    
    def staff_index_of_durable(self, durable: Durable) -> int:
        """Returns the staff index (zero-based) of the given durable
        with respect to the whole score (all the instruments) (to the system)"""
        staff = StaffSemantic.of_durable(durable)
        measure = Measure.of_staff(staff)
        part = Part.of_measure(measure)

        assert part in self.parts, "Given part must be in this score"
        
        return self.first_staff_index_of_part(part) + staff.staff_index
    
    def get_score_measure(self, measure_index: int) -> ScoreMeasure:
        """
        Returns a view of the score from an all-parts temporal perspective.
        This view is constructed each time you call this method and is not
        stored in the data model.
        """
        return ScoreMeasure.from_part_measures([
            self.parts[i].measures[measure_index]
            for i in range(len(self.parts))
        ])

    def validate(self):
        "Runs various consistency validation checks on the entire score"
        self._validate_consistent_measure_count()
        
        for p in self.parts:
            p.validate()
    
    def _validate_consistent_measure_count(self):
        """All parts must have the same number of measures"""
        counts = [len(p.measures) for p in self.parts]
        
        if len(counts) == 0:
            return
        
        first_count = counts[0]
        for c in counts:
            if c != first_count:
                raise Exception(
                    "The score's parts have differing number of measures."
                )
