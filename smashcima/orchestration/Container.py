from types import FunctionType
import punq
from typing import Callable, List, Optional, Set, TypeVar, Type, Union


T = TypeVar("T")
U = TypeVar("U", bound=T)


class MissingInterfaceBindingTargetError(Exception):
    """Raised if we are binding an interface to a type
    that is not yet registered."""
    pass


class Container:
    """
    Service container used for Model services. Since it's meant to be used
    in the context of a single model, it by default registers all services
    as singletons, since it's unlikely there would be required any transients.
    """

    def __init__(self, register_itself=True) -> None:
        self._container = punq.Container()
        self._registered_types: Set[Type] = set()

        # register the container itself into the container
        if register_itself:
            self.instance(Container, self)
    
    @property
    def registered_types(self) -> List[Type]:
        """Returns all types that are registered in the container"""
        return list(self._registered_types)
    
    def instance(self, instance_type: Type[T], instance: T):
        """Registers an existing instance to be used for a given service type.
        
        :param instance_type: The service type the instance should be bound to.
        :param instance: The instance that should be returned when resolving.
        """
        self._registered_types.add(instance_type)
        self._container.register(
            service=instance_type,
            instance=instance
        )

    def type(self, concrete_type: Type[T]):
        """Registers a type to be resolvable by the container.

        The type will be constructed during its first resolution and then kept
        around as a singleton instance.
        
        :param concrete_type: The type to be registered.
        """
        self._registered_types.add(concrete_type)
        self._container.register(
            service=concrete_type,
            scope=punq.Scope.singleton
        )

    def interface(
        self,
        abstract_type: Type,
        concrete_type_or_factory: Union[Type, Callable[..., T]],
        register_impl=False
    ):
        """Registers an implementation to be used for an interface.

        The type will be constructed during its first resolution and then kept
        around as a singleton instance.

        :param abstract_type: The abstract interface type.
        :param concrete_type_or_factory: The specific type to be used for the interface.
            Or a factory that constructs or resolves the concrete instance.
        :param register_impl: If true, the specific type implementation is
            also registered into the container.
        """
        # if a factory is given, register it as a factory
        if isinstance(concrete_type_or_factory, FunctionType):
            self.factory(abstract_type, concrete_type_or_factory)
            return

        # now we have a type given
        concrete_type: Type = concrete_type_or_factory # type: ignore
        assert issubclass(concrete_type, abstract_type)
        
        # register the implementation type as well, if requested
        if register_impl:
            self.type(concrete_type)

        # make sure the implementation type is registered
        if not self.has(concrete_type):
            raise MissingInterfaceBindingTargetError

        # register the interface as a resolution alias
        # (the interface type just points to a concrete type)
        self.factory(abstract_type, lambda: self.resolve(concrete_type))
    
    def factory(self, concrete_type: Type[T], factory: Callable[..., T]):
        """Registers a factory to be used for a type resolution.
        
        The factory's arguments will be resolved by the container.

        :param concrete_type: The type to be resolved.
        :param factory: The factory that constructs that type.
        """
        self._registered_types.add(concrete_type)
        self._container.register(
            service=concrete_type,
            factory=factory,
            scope=punq.Scope.singleton
        )
    
    def resolve(self, resolve_type: Type[T]) -> T:
        """Constructs or returns an already constructed instance of type.
        
        :param resolve_type: The type to construct.
        """
        return self._container.resolve(resolve_type)

    def has(self, resolve_type: Type) -> bool:
        """Returns true if the given type can be resolved (has been registered).
        
        :param resolve_type: The type to resolve.
        """
        return resolve_type in self._registered_types
