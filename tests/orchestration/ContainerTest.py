from typing import Optional
import unittest
from smashcima.orchestration.Container import Container
import punq
import abc


class _MyAbstractInterface(abc.ABC):
    pass


class _MyCoreService(_MyAbstractInterface):
    pass


class _MyChildService:
    def __init__(self, core: _MyCoreService):
        self.core = core


class _MyChildServiceWithInterface:
    def __init__(self, core: _MyAbstractInterface):
        self.core = core


class ContainerTest(unittest.TestCase):
    def test_it_can_construct_services(self):
        c = Container()

        # fails if not registered
        with self.assertRaises(punq.MissingDependencyError):
            c.resolve(_MyCoreService)

        # register
        c.type(_MyCoreService)

        # now resolution succeeds
        core = c.resolve(_MyCoreService)
        assert isinstance(core, _MyCoreService)
    
    def test_it_can_construct_services_with_dependencies(self):
        c = Container()

        c.type(_MyCoreService)
        c.type(_MyChildService)

        child = c.resolve(_MyChildService)
        assert isinstance(child, _MyChildService)
        assert isinstance(child.core, _MyCoreService)
    
    def test_it_can_resolve_service_via_interface(self):
        c = Container()

        c.interface(_MyAbstractInterface, _MyCoreService)

        # we can resolve the interface and we get the service
        core = c.resolve(_MyAbstractInterface)
        assert isinstance(core, _MyCoreService)

        # but we cannot resolve the service directly
        with self.assertRaises(punq.MissingDependencyError):
            c.resolve(_MyCoreService)
    
    def test_it_can_resolve_service_with_interface_dependency(self):
        c = Container()

        c.interface(_MyAbstractInterface, _MyCoreService)
        c.type(_MyChildServiceWithInterface)

        child = c.resolve(_MyChildServiceWithInterface)
        assert isinstance(child, _MyChildServiceWithInterface)
        assert isinstance(child.core, _MyCoreService)
    
    def test_it_can_resolve_instance(self):
        c = Container()

        core = _MyCoreService()
        c.instance(_MyCoreService, core)

        assert c.resolve(_MyCoreService) is core
    
    def test_it_registers_instances_as_singletons(self):
        c = Container()

        core = _MyCoreService()
        c.instance(_MyCoreService, core)

        # resolve twice and get the same instance
        assert c.resolve(_MyCoreService) is core
        assert c.resolve(_MyCoreService) is core
    
    def test_it_registers_types_as_singletons(self):
        c = Container()
        c.type(_MyCoreService)

        core = c.resolve(_MyCoreService)

        assert c.resolve(_MyCoreService) is core
        assert c.resolve(_MyCoreService) is core
    
    def test_it_registers_interfaces_as_singletons(self):
        c = Container()
        c.interface(_MyAbstractInterface, _MyCoreService)

        core = c.resolve(_MyAbstractInterface)
        assert isinstance(core, _MyCoreService)
        
        assert c.resolve(_MyAbstractInterface) is core
        assert c.resolve(_MyAbstractInterface) is core
    
    def test_it_resolves_itself(self):
        c = Container(register_itself=True)
        resolved = c.resolve(Container)
        assert resolved is c
    
    def test_it_can_prevent_self_registration(self):
        c = Container(register_itself=False)
        with self.assertRaises(punq.MissingDependencyError):
            c.resolve(Container)

    def test_it_can_register_interface_via_factory(self) -> None:
        c = Container()
        core: Optional[_MyCoreService] = None

        def _factory():
            nonlocal core
            core = _MyCoreService()
            return core

        c.factory(_MyAbstractInterface, _factory)

        assert core is None

        resolved = c.resolve(_MyAbstractInterface)

        assert core is not None
        assert resolved is core
