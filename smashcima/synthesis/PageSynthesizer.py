import abc

from smashcima.geometry.Vector2 import Vector2
from smashcima.scene.visual.Page import Page


class PageSynthesizer(abc.ABC):
    """Represents an interface to a synthesizer that produces pages of
    empty staves onto which notation can be written (synthesized)"""

    @abc.abstractmethod    
    def synthesize_page(self, page_origin: Vector2) -> Page:
        """Creates a new page object with its upper left corner at the given
        origin point (in the scene coordinates) and with size depending
        on the specific implementation of this page synthesizer"""
        raise NotImplementedError
