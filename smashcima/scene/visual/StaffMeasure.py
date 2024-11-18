from dataclasses import dataclass

from ..LabeledRegion import LabeledRegion
from ..SceneObject import SceneObject
from ..semantic.Measure import Measure
from ..semantic.StaffSemantic import StaffSemantic
from ..SmashcimaLabels import SmashcimaLabels
from .StaffVisual import StaffVisual


@dataclass
class StaffMeasure(SceneObject):
    """Region in the score representing a measure on one staff"""

    measure: Measure
    """Semantic measure this visual staff measure represents a part of"""

    staff_semantic: StaffSemantic
    """Which semantic staff of the measure do we represent"""

    staff_visual: StaffVisual
    """Which visual staff does this staff measure sit on"""

    region: LabeledRegion
    """The region encapsulating the staff measure"""

    def __post_init__(self):
        assert self.region.label == SmashcimaLabels.staffMeasure.value, \
            "Staff measure region must have proper classification label"

    @classmethod
    def of_staff_semantic(cls, staff_semantic: StaffSemantic):
        return cls.of(staff_semantic, lambda sm: sm.staff_semantic)

    @classmethod
    def many_of_staff_visual(cls, staff_visual: StaffVisual):
        return cls.many_of(staff_visual, lambda sm: sm.staff_visual)
