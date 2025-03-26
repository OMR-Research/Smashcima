from ..geometry.Vector2 import Vector2
from ..scene.AffineSpace import AffineSpace
from ..scene.visual.StaffVisual import StaffVisual
import abc


class StafflinesSynthesizer(abc.ABC):
    """Interface for a stafflines synthesizer"""

    @property
    @abc.abstractmethod
    def staff_height(self) -> float:
        """Returns the average height of synthesized staff in millimeters"""
        raise NotImplementedError

    @abc.abstractmethod
    def synthesize_stafflines(
        self,
        page_space: AffineSpace,
        position: Vector2,
        width: float,
    ) -> StaffVisual:
        """Synthesizes a new StaffVisual object.

        :param page_space: Stafflines will be placed into this space.
        :param position: Position of the left endpoint of the middle staffline.
        :param width: Width of the staff in millimeters.
        """
        raise NotImplementedError
