import unittest
from smashcima.scene.nameof_via_dummy import nameof_via_dummy


class Foo:
    def __init__(self):
        self.bar = "BAR!"


class NameofViaDummyTest(unittest.TestCase):
    def test_it_gets_name(self):
        assert nameof_via_dummy(Foo, lambda f: f.bar) == "bar"
    
    def test_it_gets_made_up_field(self):
        assert nameof_via_dummy(Foo, lambda f: f.asd) == "asd"
    
    def test_it_survives_non_string(self):
        assert nameof_via_dummy(Foo, lambda f: "nah") == "nah"
        assert nameof_via_dummy(Foo, lambda f: 42) == "42"
