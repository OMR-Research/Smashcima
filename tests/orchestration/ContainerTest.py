import abc
import unittest
from typing import Optional

import punq

from smashcima.orchestration.Container import (
    Container, MissingInterfaceBindingTargetError)


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

        # check it can not be resolved
        assert not c.has(_MyCoreService)

        # register
        c.type(_MyCoreService)

        # check it can be resolved
        assert c.has(_MyCoreService)

        # now resolution succeeds
        core = c.resolve(_MyCoreService)
        assert isinstance(core, _MyCoreService)
    
    def test_it_can_construct_services_with_dependencies(self):
        c = Container()

        c.type(_MyCoreService)
        c.type(_MyChildService)

        # check it can be resolved
        assert c.has(_MyCoreService)
        assert c.has(_MyChildService)

        child = c.resolve(_MyChildService)
        assert isinstance(child, _MyChildService)
        assert isinstance(child.core, _MyCoreService)
    
    def test_it_can_resolve_service_via_interface(self):
        c = Container()

        # we cannot bind interface to a type without first registering that type
        with self.assertRaises(MissingInterfaceBindingTargetError):
            c.interface(_MyAbstractInterface, _MyCoreService)
        
        # register the implementation type
        c.type(_MyCoreService)

        # now can bind the interface
        c.interface(_MyAbstractInterface, _MyCoreService)

        # check both can be resolved
        assert c.has(_MyCoreService)
        assert c.has(_MyAbstractInterface)

        # we can resolve the interface and we get the service
        core = c.resolve(_MyAbstractInterface)
        assert isinstance(core, _MyCoreService)

        # but can also resolve the service directly and it's the same one
        assert c.resolve(_MyCoreService) is core
    
    def test_it_can_resolve_service_with_interface_dependency(self):
        c = Container()

        c.interface(_MyAbstractInterface, _MyCoreService, register_impl=True)
        c.type(_MyChildServiceWithInterface)

        # check all can be resolved
        assert c.has(_MyCoreService)
        assert c.has(_MyAbstractInterface)
        assert c.has(_MyChildServiceWithInterface)

        child = c.resolve(_MyChildServiceWithInterface)
        assert isinstance(child, _MyChildServiceWithInterface)
        assert isinstance(child.core, _MyCoreService)
    
    def test_it_can_resolve_instance(self):
        c = Container()

        core = _MyCoreService()
        c.instance(_MyCoreService, core)

        assert c.has(_MyCoreService)

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
        c.interface(_MyAbstractInterface, _MyCoreService, register_impl=True)

        core = c.resolve(_MyAbstractInterface)
        assert isinstance(core, _MyCoreService)
        
        assert c.resolve(_MyAbstractInterface) is core
        assert c.resolve(_MyAbstractInterface) is core
    
    def test_it_resolves_itself(self):
        c = Container(register_itself=True)
        assert c.has(Container)
        resolved = c.resolve(Container)
        assert resolved is c
    
    def test_it_can_prevent_self_registration(self):
        c = Container(register_itself=False)
        assert not c.has(Container)
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

        assert not c.has(_MyCoreService)
        assert c.has(_MyAbstractInterface)

        resolved = c.resolve(_MyAbstractInterface)

        assert core is not None
        assert resolved is core
    
    def test_it_can_register_factory_via_interface(self) -> None:
        c = Container()
        core: Optional[_MyCoreService] = None

        def _factory():
            nonlocal core
            core = _MyCoreService()
            return core

        c.interface(_MyAbstractInterface, _factory)

        assert core is None

        assert not c.has(_MyCoreService)
        assert c.has(_MyAbstractInterface)

        resolved = c.resolve(_MyAbstractInterface)

        assert core is not None
        assert resolved is core
