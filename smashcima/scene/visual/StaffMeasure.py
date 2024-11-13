from dataclasses import dataclass

from ..SceneObject import SceneObject
from ..Region import Region


@dataclass
class StaffMeasure(SceneObject):
    region: Region

    # TODO: this is a sketch of a region to be detected
    # also add:
    # SystemMeasure
    # Grandstaff
    #
    # and implement System
