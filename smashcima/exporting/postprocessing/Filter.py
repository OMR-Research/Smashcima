import random
from abc import ABC, abstractmethod

from ..image.ImageLayer import ImageLayer


class Filter(ABC):
    """Base class for a postprocessing filter that can be applied
    to an ImageLayer"""
    def __init__(self, rng: random.Random, p=1.0):
        self.rng = rng
        """The random number generator used to control randomness"""

        self.force_do = False
        """Force the filter to DO run"""

        self.force_dont = False
        """Force the filter to do NOT run"""

        self.p = p
        """Probability that the filter will be applied"""
    
    def __call__(self, input: ImageLayer) -> ImageLayer:
        assert not self.force_do or not self.force_dont, \
            "You cannot both force a filter to DO and DON'T run."
        
        if self.force_dont:
            return input
        
        if self.force_do or self.rng.random() < self.p:
            return self.apply_to(input)
        else:
            return input
    
    @abstractmethod
    def apply_to(self, input: ImageLayer) -> ImageLayer:
        """Implements the filter"""
        raise NotImplementedError
