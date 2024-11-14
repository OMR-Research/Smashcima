from typing import Any, Type, TypeVar, List, Optional
from dataclasses import dataclass, field


T = TypeVar("T")


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
    
    def get_inlinked(
        self,
        obj_type: Type[T],
        name: Optional[str] = None,
        at_most_one=False,
        fail_if_none=False
    ) -> List[T] | Optional[T] | T:
        """Returns scene objects that link to this object (called sources)
        
        obj_type: What source types are we interested in
        name: Through which field on the source is the link facilitated
        at_most_one: Returns the first found source, fails if there are more.
        """

        # TODO: this is absolutely dismal with mypy, instead provide:
        # Foo.of_bar() -> Foo
        # Foo.of_bar_or_none() -> Optional[Foo]
        # Foo.many_of_bar() -> List[Foo]

        sources = [
            link.source for link in self.inlinks
            if isinstance(link.source, obj_type)
                and (name is None or link.name == name)
        ]

        if fail_if_none:
            if len(sources) == 0:
                raise Exception(
                    f"There are no {obj_type} linking to " + \
                    f"{type(self)} via name {name}."
                )

        if at_most_one:
            if len(sources) > 1:
                raise Exception(
                    f"There are more than one {obj_type} linking to " + \
                    f"{type(self)} via name {name}."
                )
            if len(sources) == 0:
                return None
            else:
                return sources[0]
        
        return sources
