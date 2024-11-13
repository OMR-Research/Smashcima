from dataclasses import dataclass

from .Region import Region


@dataclass
class LabeledRegion(Region):
    """Scene region with a classification label.

    Represents a region in the scene that could be recognized in
    an object detection task.

    It is defined by a set of polygons, because a polygon can undergo affine
    transformations and remain a polygon (unlike a bounding box).
    Other lower-detail regions can be derived from the set of polygons easily
    (e.g. convex hull, tight rectangle, bounding box).
    """

    label: str
    """Label for the object classification task"""

    def __post_init__(self):
        assert type(self.label) is str, "Label must be a string"
