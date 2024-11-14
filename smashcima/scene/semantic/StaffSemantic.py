from dataclasses import dataclass, field
from ..SceneObject import SceneObject
from typing import List
from .Durable import Durable


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

    @classmethod
    def of_durable(cls, durable: Durable):
        return cls.of(durable, lambda s: s.durables)
