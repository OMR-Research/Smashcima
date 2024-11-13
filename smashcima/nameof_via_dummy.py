from typing import Any, Callable, Type, TypeVar


T = TypeVar("T")


class _Dummy:
    """
    Dummy class: When you get any attribute, it returns that attributes name
    """
    def __getattribute__(self, name: str) -> Any:
        return name


def nameof_via_dummy(examined_type: Type[T], probe: Callable[[T], Any]) -> str:
    """Get the name of an object property via a lambda function by substituting
    a dummy instance instead of the real examined type.
    
    Can be used like this:
    nameof_via_dummy(MyType, lambda my_type: my_type.my_property)
    """
    return str(probe(_Dummy())) # type: ignore


if __name__ == "__main__":
    class Foo:
        def __init__(self):
            self.bar = "BAR!"
    
    assert nameof_via_dummy(Foo, lambda f: f.bar) == "bar"

    print("OK!")
