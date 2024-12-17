import punq
from typing import Callable, TypeVar, Type


T = TypeVar("T")
U = TypeVar("U", bound=T)


class Container:
    """
    Service container used for Model services. Since it's meant to be used
    in the context of a single model, it by default registers all services
    as singletons, since it's unlikely there would be required any transients.
    """

    def __init__(self, register_itself=True):
        self._container = punq.Container()

        # register the container itself into the container
        if register_itself:
            self.instance(Container, self)
    
    def instance(self, instance_type: Type[T], instance: T):
        """Registers an existing instance to be used for a given service type.
        
        :param instance_type: The service type the instance should be bound to.
        :param instance: The instance that should be returned when resolving.
        """
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
        self._container.register(
            service=concrete_type,
            scope=punq.Scope.singleton
        )

    def interface(self, abstract_type: Type, concrete_type: Type):
        """Registers an implementation to be used for an interface.

        The type will be constructed during its first resolution and then kept
        around as a singleton instance.

        :param abstract_type: The abstract interface type.
        :param concrete_type: The specific type to be used for the interface.
        """
        assert issubclass(concrete_type, abstract_type)
        self._container.register(
            service=abstract_type,
            factory=concrete_type,
            scope=punq.Scope.singleton
        )
    
    def factory(self, concrete_type: Type[T], factory: Callable[..., T]):
        """Registers a factory to be used for a type resolution.
        
        The factory's arguments will be resolved by the container.

        :param concrete_type: The type to be resolved.
        :param factory: The factory that constructs that type.
        """
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
