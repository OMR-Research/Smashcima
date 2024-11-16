import abc

from .AffineSpace import AffineSpace
from .SceneObject import SceneObject

try:
    from typing import Self  # type: ignore
except:
    from typing_extensions import Self


class AffineSpaceVisitor(abc.ABC):
    """Base class for walking through the scene hierarchy"""
    def __init__(self, space: AffineSpace):
        self.space = space

    def run(self):
        """Executes the tree visiting algorithm"""
        # IMPORTANT: Iterate in the oder in which inlinks are listed!
        for link in self.space.inlinks:
            if isinstance(link.source, AffineSpace):
                sub_visitor = self.create_sub_visitor(link.source)
                sub_visitor.run()
                self.accept_sub_visitor(sub_visitor)
            else:
                self.visit_scene_object(link.source)
    
    @abc.abstractmethod
    def create_sub_visitor(self, sub_space: AffineSpace) -> Self:
        """Creates the visitor instance for a sub space"""
        raise NotImplementedError

    @abc.abstractmethod
    def accept_sub_visitor(self, sub_visitor: Self):
        """Once sub space visiting finished, incorporate its results"""
        raise NotImplementedError

    @abc.abstractmethod
    def visit_scene_object(self, obj: SceneObject):
        """Handle scene objects that are children but are not affine spaces"""
        raise NotImplementedError
