import abc
from typing import List

from smashcima.scene.AffineSpace import AffineSpace
from smashcima.scene.semantic.Score import Score
from smashcima.scene.visual.Page import Page
from smashcima.scene.visual.StaffVisual import StaffVisual
from smashcima.scene.visual.System import System


class MusicNotationSynthesizer(abc.ABC):
    """Represents an interface to a synthesizer that places music notation
    onto empty staves in a pre-synthesized page."""
    
    @abc.abstractmethod
    def fill_page(
        self,
        page: Page,
        score: Score,
        start_on_measure: int
    ) -> List[System]:
        """Fills the page with music and returns the list of synthesized systems"""
        raise NotImplementedError

    @abc.abstractmethod
    def synthesize_system(
        self,
        page_space: AffineSpace,
        staves: List[StaffVisual],
        score: Score,
        start_on_measure: int
    ) -> System:
        """Synthesizes a single system of music onto the provided staves"""
        raise NotImplementedError
