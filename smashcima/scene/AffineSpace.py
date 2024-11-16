from dataclasses import dataclass
from typing import List, Optional

from ..geometry.Transform import Transform
from .SceneObject import SceneObject


@dataclass
class AffineSpace(SceneObject):
    """
    Affine spaces define the visual hierarchy of the scene. Only visual elements
    require their presence. Their hierarchy allows for defining local spatial
    relationships in local coordinate systems. 2D affine transforms are used
    to traverse the affine space hierarchy.
    """

    parent_space: Optional["AffineSpace"] = None
    "What other space does this space belong under"

    transform: Transform = Transform.identity()
    """Transform that translates from this space's local coordinates
    to the parent's space coordinates, effectively defining the placement of
    this space within the parent space."""

    def get_children(self) -> List["AffineSpace"]:
        """Returns child affine spaces as a list"""
        return AffineSpace.many_of(self, lambda s: s.parent_space)
    
    def get_root(self) -> "AffineSpace":
        """Returns the top-most root affine space"""
        space = self
        while space.parent_space is not None:
            space = space.parent_space
        return space

    def transform_from(self, sub_space: "AffineSpace") -> Transform:
        """Returns the transform from the given space to the current space"""
        if sub_space is None:
            raise ValueError("The given space should not be None")
        
        t = Transform.identity()
        s: Optional[AffineSpace] = sub_space
        
        while s is not None:
            if s is self:
                return t
            
            t = t.then(s.transform)
            s = s.parent_space

        raise Exception("The given sub space is not attached under this space")
