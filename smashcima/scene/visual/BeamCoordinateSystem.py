from ..semantic.StemValue import StemValue
from ..semantic.BeamedGroup import BeamedGroup
from ..AffineSpace import AffineSpace
from smashcima.geometry.Point import Point
from ..SceneObject import SceneObject


class BeamCoordinateSystem(SceneObject):
    """Defines the placement and slope of a beamed group. All values are in the
    paper coordinate system (paper space)."""

    def __init__(
        self,
        beamed_group: BeamedGroup,
        page_space: AffineSpace,
        k: float,
        q: float,
        beam_spacing: float
    ):
        """Initialize the coordinate system as a linear function over the
        paper space.
        
        :param beamed_group: The semantic beamed group that is described by this.
        :param space: The paper space in which all the computations occur.
        :param k: The slope of the line (rise over run).
        :param q: The value of Y at X=0.
        :param beam_spacing: Separation between beams in millimeters.
        """
        super().__init__()
        
        self.beamed_group = beamed_group
        self.page_space = page_space
        self.k = k
        self.q = q
        self.beam_spacing = beam_spacing
    
    @classmethod
    def of_beamed_group(cls, beamed_group: BeamedGroup):
        return cls.of(beamed_group, lambda bcs: bcs.beamed_group)
    
    def __call__(
        self,
        x: float,
        beam_number: int = 1,
        stem_value: StemValue = StemValue.up
    ) -> float:
        """The coordinate system acts like a linear function over the paper
        space, so that when you give it X coordinate, it will give you the Y
        vertical coordinate of the main beam (unless you also specify which
        beam you are interested in, and from which direction is the stem
        comming in)."""
        assert beam_number >= 1, type(beam_number) is int

        beam_index = (beam_number - 1)
        
        if stem_value == StemValue.down:
            beam_index *= -1

        return self.k * x + self.q + (beam_index * self.beam_spacing)
    
    def point(
        self,
        x: float,
        beam_number: int = 1,
        stem_value: StemValue = StemValue.up
    ):
        """Invokes the linear function and instead of returning just Y,
        it returns the whole [X, Y] point"""
        return Point(x, self(x, beam_number, stem_value))
