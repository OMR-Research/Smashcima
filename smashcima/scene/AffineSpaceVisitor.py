import abc
from typing import TypeVar

from .AffineSpace import AffineSpace
from .SceneObject import SceneObject

T = TypeVar("T", bound="AffineSpaceVisitor")


class AffineSpaceVisitor(abc.ABC):
    """Base class for walking through the scene hierarchy"""
    def __init__(self, space: AffineSpace):
        self.space = space

    def run(self):
        """Executes the tree visiting algorithm"""
        # IMPORTANT: Iterate in the order in which inlinks are listed!
        for link in self.space.inlinks:
            if isinstance(link.source, AffineSpace):
                sub_visitor = self.create_sub_visitor(link.source)
                sub_visitor.run()
                self.accept_sub_visitor(sub_visitor)
            else:
                self.visit_scene_object(link.source)
    
    @abc.abstractmethod
    def create_sub_visitor(self: T, sub_space: AffineSpace) -> T:
        """Creates the visitor instance for a sub space"""
        raise NotImplementedError

    @abc.abstractmethod
    def accept_sub_visitor(self: T, sub_visitor: T):
        """Once sub space visiting finished, incorporate its results"""
        raise NotImplementedError

    @abc.abstractmethod
    def visit_scene_object(self, obj: SceneObject):
        """Handle scene objects that are children but are not affine spaces"""
        raise NotImplementedError
