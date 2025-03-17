import random
from typing import Iterable

from .Filter import Filter


class FilterStack(Filter):
    """A set of filters that are applied successively"""
    def __init__(self, filters: Iterable[Filter], rng: random.Random, p=1.0):
        super().__init__(rng, p)
        self.filters = list(filters)

    def apply_to(self, input):
        layer = input
        for filter in self.filters:
            layer = filter(layer)
        return layer
