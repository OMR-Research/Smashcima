from typing import Any, Callable, Tuple, Type, TypeVar, List, Optional
from dataclasses import dataclass, field

from smashcima.scene.nameof_via_dummy import nameof_via_dummy


T = TypeVar("T", bound="SceneObject")


class SceneRelationshipResolutionException(Exception):
    """Thrown by the `.of`, `.many_of`, and `.of_or_none` query methods"""
    pass


class Link:
    """Describes a named, oriented link between two scene objects"""
    source: "SceneObject"
    target: "SceneObject"
    name: str

    def __init__(self, source: "SceneObject", target: "SceneObject", name: str):
        self.source = source
        self.target = target
        self.name = name
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Link):
            return False
        if self.source is not other.source:
            return False
        if self.target is not other.target:
            return False
        if self.name != other.name:
            return False
        return True
    
    def __repr__(self) -> str:
        return f"{self.source.__class__.__name__}-->" + \
            f"{self.target.__class__.__name__}"

    def attach(self):
        """Add the link into the graph"""
        self.source.outlinks.append(self)
        self.target.inlinks.append(self)

    def detach(self):
        """Remove the link from the graph"""
        self.source.outlinks.remove(self)
        self.target.inlinks.remove(self)


@dataclass
class SceneObject:
    inlinks: List[Link] = field(default_factory=list, init=False, repr=False)
    outlinks: List[Link] = field(default_factory=list, init=False, repr=False)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "inlinks":
            pass
        elif name == "outlinks":
            pass
        elif isinstance(value, SceneObject):
            self._destroy_outlinks_for(name)
            Link(source=self, target=value, name=name).attach()
        elif isinstance(value, list) or isinstance(value, set):
            # TODO: hook into mutation methods or freeze the instances!
            self._destroy_outlinks_for(name)
            for item in value:
                if isinstance(item, SceneObject):
                    Link(source=self, target=item, name=name).attach()
        else:
            self._destroy_outlinks_for(name)

        super().__setattr__(name, value)
    
    def _destroy_outlinks_for(self, name: str):
        for link in list(self.outlinks):
            if link.name == name:
                link.detach()

    ########################
    # Relationship queries #
    ########################

    @classmethod
    def _of_impl(
        cls: Type[T],
        subject: "SceneObject",
        name_probe: Callable[[T], Any]
    ) -> Tuple[List[T], str]:
        name = nameof_via_dummy(cls, name_probe)
        return (
            [
                link.source for link in subject.inlinks
                if isinstance(link.source, cls)
                    and (name is None or link.name == name)
            ],
            name
        )

    @classmethod
    def of(
        cls: Type[T], 
        subject: "SceneObject",
        name_probe: Callable[[T], Any]
    ) -> T:
        """Uses scene graph links to resolve a `cls` type instance linking
        to `subject` via a field name resolved from the `name_probe`.
        Raises an exception if there is no scene object to be found or
        if there are more than one object found.

        :param subject: The inlinked object we start from.
        :param name_probe: Lambda that given a `cls` type (dummy) instance
        returns the field to be used for link name. It can also return string
        to be used directly as the link name.
        :returns: An outlinked object, linking to `subject` via `name`.
        """
        if subject is None:
            raise ValueError("Passed in subject cannot be None")
        
        candidates, name = cls._of_impl(subject, name_probe)
        
        if len(candidates) > 1:
            raise SceneRelationshipResolutionException(
                f"There are more than one {cls} linking to " + \
                f"{subject} via name {name}."
            )
        
        if len(candidates) == 0:
            raise SceneRelationshipResolutionException(
                f"There are no {cls} linking to " + \
                f"{subject} via name {name}."
            )
        
        return candidates[0]

    @classmethod
    def of_or_none(
        cls: Type[T],
        subject: Optional["SceneObject"],
        name_probe: Callable[[T], Any]
    ) -> Optional[T]:
        """Uses scene graph links to resolve a `cls` type instance linking
        to `subject` via a field name resolved from the `name_probe`.
        If there is no such object found, it returns None.
        Raises an exception if there are more than one object found.

        :param subject: The inlinked object we start from.
        :param name_probe: Lambda that given a `cls` type (dummy) instance
        returns the field to be used for link name. It can also return string
        to be used directly as the link name.
        :returns: An outlinked object, linking to `subject` via `name` or `None`.
        """
        if subject is None:
            return None
        
        candidates, name = cls._of_impl(subject, name_probe)
        
        if len(candidates) > 1:
            raise SceneRelationshipResolutionException(
                f"There are more than one {cls} linking to " + \
                f"{subject} via name {name}."
            )
        
        if len(candidates) == 0:
            return None
        
        return candidates[0]

    @classmethod
    def many_of(
        cls: Type[T],
        subject: "SceneObject",
        name_probe: Callable[[T], Any]
    ) -> List[T]:
        """Uses scene graph links to resolve a list of `cls` type instances
        linking to `subject` via a field name resolved from the `name_probe`.

        :param subject: The inlinked object we start from.
        :param name_probe: Lambda that given a `cls` type (dummy) instance
        returns the field to be used for link name. It can also return string
        to be used directly as the link name.
        :returns: A list of outlinked objects, linking to `subject` via `name`.
        """
        if subject is None:
            raise ValueError("Passed in subject cannot be None")
        
        candidates, _ = cls._of_impl(subject, name_probe)
        
        return candidates
