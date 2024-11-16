from dataclasses import dataclass

from smashcima.geometry import Rectangle

from .AffineSpace import AffineSpace
from .SceneObject import SceneObject


@dataclass
class ViewBox(SceneObject):
    """Viewport into the scene, used for framing exports."""

    space: AffineSpace
    """The space in which the view is placed"""

    rectangle: Rectangle
    """The rectangular position of the view in its space"""
