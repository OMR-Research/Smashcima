from dataclasses import dataclass

from smashcima.geometry import Contours, Rectangle

from .AffineSpace import AffineSpace
from .SceneObject import SceneObject


@dataclass
class Region(SceneObject):
    """A region with an area inside the scene.

    A region can be transformed through the affine space hierarchy
    and can be used for various area-describing tasks (object localization,
    masking, etc.).

    It is defined by a set of polygons, because a polygon can undergo affine
    transformations and remain a polygon (unlike a bounding box).
    Other lower-detail regions can be derived from the set of polygons easily
    (e.g. convex hull, tight rectangle, bounding box).
    """

    space: AffineSpace
    """Space in which the region is situated. Not owned by the region."""

    contours: Contours
    """Polygon areas that define the region (in parent space coordinates)"""

    def detach(self):
        """Unlink the region from the scene"""
        self.space = None

    @classmethod
    def many_of_space(cls, space: AffineSpace):
        return cls.many_of(space, lambda r: r.space)

    def get_contours_in_space(self, target_space: AffineSpace) -> Contours:
        """Returns the contours polygons transformed to the target space
        
        :param target_space: The space to which coordinates of the contours
            should be transformed. Must be an ancestor of this region's space.
        """
        transform = target_space.transform_from(self.space)
        return transform.apply_to(self.contours)

    def get_bbox_in_space(self, target_space: AffineSpace) -> Rectangle:
        """Returns the bounding box rectangle in the target space coordinates
        
        :param target_space: The space to which coordinates of the contours
            should be transformed. Must be an ancestor of this region's space.
        """
        return self.get_contours_in_space(target_space).bbox()
