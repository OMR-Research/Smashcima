from dataclasses import dataclass
from typing import List

from ..LabeledRegion import LabeledRegion
from ..SceneObject import SceneObject
from ..semantic.ScoreMeasure import ScoreMeasure
from ..SmashcimaLabels import SmashcimaLabels
from .StaffMeasure import StaffMeasure


@dataclass
class SystemMeasure(SceneObject):
    """Region in the score representing a measure of a system (all staves)"""

    score_measure: ScoreMeasure
    """Semantic measure in the score this visual system measure represents"""

    staff_measures: List[StaffMeasure]
    """Staff measures that make up this system measure"""

    region: LabeledRegion
    """The region encapsulating the system measure"""

    def __post_init__(self):
        assert self.region.label == SmashcimaLabels.systemMeasure.value, \
            "System measure region must have proper classification label"
