from dataclasses import dataclass, field
from ..SceneObject import SceneObject
from typing import List, Optional
from .Measure import Measure
from .Attributes import Attributes


@dataclass
class Part(SceneObject):
    """Represents a single part (an instrument) of a score"""
    
    measures: List[Measure] = field(default_factory=list)
    "A part consists of a list of measures"

    staff_count: int = 1
    "Number of staves for this part (each measure should have all of them)"

    @classmethod
    def of_measure(cls, measure: Measure):
        return cls.of(measure, lambda p: p.measures)

    def append_measure(self, measure: Measure):
        self.measures = [*self.measures, measure]
    
    def compute_event_attributes(self) -> None:
        """Sets attributes for all events based on present attributes changes"""
        attributes: Optional[Attributes] = None

        for measure in self.measures:
            for event in measure.events:
                
                # the very first event
                if attributes is None:
                    if event.attributes_change is None:
                        raise Exception(
                            "The very first event in a part has to " + \
                            "have an attributes change"
                        )
                    attributes = Attributes.from_first_change(
                        staff_count=self.staff_count,
                        change=event.attributes_change
                    )
                    event.attributes = attributes

                # non-first event
                else:
                    if event.attributes_change:
                        attributes = attributes.apply_change(
                            event.attributes_change
                        )
                    event.attributes = attributes

    def validate(self):
        "Runs various consistency validation checks on the entire part"
        self._validate_consistent_staves()
    
    def _validate_consistent_staves(self):
        """All measures must have the same number of staves, ordered properly"""
        for mi, measure in enumerate(self.measures):
            # check count
            assert len(measure.staves) == self.staff_count, \
                f"Measure {mi} has {len(measure.staves)} staves but should " + \
                f"have {self.staff_count}"

            # check order and value
            for si in range(self.staff_count):
                assert measure.staves[si].staff_number == si + 1, \
                    f"Measure {mi} has incorrect staff numbers"
