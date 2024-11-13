from dataclasses import dataclass, field
from ..SceneObject import SceneObject
from typing import List, Optional
from .Durable import Durable
from smashcima.nameof_via_dummy import nameof_via_dummy


@dataclass
class StaffSemantic(SceneObject):
    """
    Represents a staff within a measure (e.g. piano measures have 2 staves),
    as a collection of durables
    """

    staff_number: int
    "Number of this staff, e.g. 1, 2, 3. Numbered from 1 and from the top down"

    durables: List[Durable] = field(default_factory=list)
    "Links to all durables within this staff"

    @property
    def staff_index(self) -> int:
        """Zero-based index of the staff in measure stafflines"""
        return self.staff_number - 1

    @staticmethod
    def of_durable(
        durable: Durable,
        fail_if_none=False
    ) -> Optional["StaffSemantic"] | "StaffSemantic":
        return durable.get_inlinked(
            StaffSemantic,
            nameof_via_dummy(StaffSemantic, lambda s: s.durables),
            at_most_one=True,
            fail_if_none=fail_if_none
        )
