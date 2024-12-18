import abc
from typing import Set

from smashcima.geometry import Point, Transform
from smashcima.scene import AffineSpace, Glyph


class GlyphSynthesizer(abc.ABC):
    """Interface for a glyph synthesizer"""

    @abc.abstractmethod
    def supports_label(self, label: str) -> bool:
        """Returns true if the given glyph type can be synthesized.
        
        Override this when building custom glyph synthesizers.
        """
        raise NotImplementedError

    def synthesize_glyph(
        self,
        label: str,
        parent_space: AffineSpace,
        transform: Transform
    ) -> Glyph:
        """Synthesizes a new glyph
        
        :param label: Which kind of glyph to synthesize (classification label)
        :param parent_space: The glyph will be placed into this space
        :param transform: How should the glyph be placed into the parent space
        :returns: The newly synthesized glyph instance, already attached to
            the parent space.
        """
        # check that we are not accidentally passing in an Enum instead of str
        assert type(label) is str, "The requested glyph label is not a string"

        # create a new glyph
        glyph = self.create_glyph(label)

        # check its label
        assert glyph.label == label, f"The user requested class {label} " + \
            f"but got {glyph.label} instead"
        
        # attach to the parent space
        glyph.space.parent_space = parent_space
        glyph.space.transform = transform

        return glyph

    def synthesize_glyph_at(
        self,
        label: str,
        parent_space: AffineSpace,
        point: Point
    ) -> Glyph:
        """Synthesizes a new glyph with its origin translated to a point.

        :param label: Which kind of glyh to synthesize (classification label)
        :param parent_space: The glyph will be placed into this space
        :param point: The glyph's origin will be placed over this point.
            The coordinates are relative to the parent space.
        :returns: The newly synthesized glyph instance, already attached to
            the parent space.
        """
        return self.synthesize_glyph(
            label=label,
            parent_space=parent_space,
            transform=Transform.translate(point.vector)
        )
    
    def create_glyph(self, label: str) -> Glyph:
        """Creates a new glyph instance of the specified label.

        Override this method when building custom glyph synthesizers.
        The returned glyph should have no parent space.

        :param label: The kind of glyph to create.
        """
        raise NotImplementedError
