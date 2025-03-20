from smashcima.orchestration.Container import Container
from .StyleDomain import StyleDomain
from typing import Optional, TypeVar, Type, Dict, Union


T = TypeVar("T", bound=StyleDomain)


class Styler:
    """Styler is a service responsible for dictating the style a synthetic
    data sample should be synthesized in. It orchestrates a fleet of
    style domains, where each style domain affects one aspect of the style.
    The synthesizers then access these style domains to know which style
    to use during synthesis."""

    def __init__(self, container: Optional[Container] = None) -> None:
        self.domains: Dict[Type[T], StyleDomain] = dict()
        self.container = container
        """Optional container for resolving domain instances by type"""
    
    def register_domains_from_container(self):
        """Goes over types in the service container and registers all domains"""
        if self.container is None:
            raise Exception("Container must be set for this method to work")
        
        for TRegistered in self.container.registered_types:
            if issubclass(TRegistered, StyleDomain):
                self.register_domain(TRegistered)

    def register_domain(
        self,
        domain_type: Type[T],
        domain_instance: Optional[T] = None
    ):
        """Register a specific domain instance for a given style domain type.
        This instance will be given to anyone who asks for the resolution
        of that style domain type."""
        assert issubclass(domain_type, StyleDomain)

        # get domain instance
        if domain_instance is None:
            if self.container is None:
                raise Exception(
                    "You either must provide the container or the " +
                    "instance when registering a style domain."
                )
            domain_instance = self.container.resolve(domain_type)

        # check domain instance type
        assert isinstance(domain_instance, domain_type)
        
        # prevent overwrites
        if domain_type in self.domains:
            raise Exception(
                f"The domain {domain_type} has already been registered."
            )
        
        # register
        self.domains[domain_type] = domain_instance
    
    def resolve_domain(self, domain_type: Type[T]) -> T:
        """Returns the registered instance of the given style domain"""
        assert issubclass(domain_type, StyleDomain)
        
        if domain_type not in self.domains:
            raise Exception(
                f"The domain {domain_type} has not been registered."
            )
        
        return self.domains[domain_type]

    def pick_style(self):
        """Go over all registered style domains and let each of them
        pick a style."""
        for domain in self.domains.values():
            domain.pick_style()
