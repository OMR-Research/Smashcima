from typing import TypeVar, Type, Optional, List, Dict
from .AffineSpace import AffineSpace
from .SceneObject import SceneObject


T = TypeVar("T", bound=SceneObject)


class Scene:
    """A scene is a collection of scene objects"""

    def __init__(self, root_space: AffineSpace):
        assert root_space.parent_space is None, \
            "Root space of a scene must have no parent"

        self.root_space = root_space
        "The global space of the scene (parent of all other spaces)"

        self.objects: Dict[int, SceneObject] = {}
        "Tracks all scene objects"

        # add the root space into the scene as a scene object
        self.add(self.root_space)
    
    def has(self, obj: SceneObject) -> bool:
        return id(obj) in self.objects

    def add(
        self,
        obj: SceneObject,
        skip_if_added=True,
        recurse_via_inlinks=True,
        recurse_via_outlinks=True
    ):
        if skip_if_added and self.has(obj):
            return

        self.objects[id(obj)] = obj
        
        # recursion down
        if recurse_via_outlinks:
            for link in obj.outlinks:
                self.add(
                    link.target,
                    skip_if_added=True,
                    recurse_via_inlinks=recurse_via_inlinks,
                    recurse_via_outlinks=recurse_via_outlinks
                )

        # recursion up
        if recurse_via_inlinks:
            for link in obj.inlinks:
                self.add(
                    link.source,
                    skip_if_added=True,
                    recurse_via_inlinks=recurse_via_inlinks,
                    recurse_via_outlinks=recurse_via_outlinks
                )
    
    def add_many(
        self,
        objs: List[SceneObject],
        skip_if_added=True,
        recurse_via_inlinks=True,
        recurse_via_outlinks=True
    ):
        for obj in objs:
            self.add(
                obj,
                skip_if_added=skip_if_added,
                recurse_via_inlinks=recurse_via_inlinks,
                recurse_via_outlinks=recurse_via_outlinks
            )
    
    def add_closure(self):
        """Add all scene objects linked from already added scene objects"""
        for obj in list(self.objects.values()):
            self.add(obj, skip_if_added=False)

    def find(self, obj_type: Type[T]) -> List[T]:
        return [
            obj for obj in self.objects.values()
            if isinstance(obj, obj_type)
        ]
