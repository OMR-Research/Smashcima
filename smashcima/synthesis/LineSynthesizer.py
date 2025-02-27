import abc
from typing import Set

import cv2
import numpy as np

from smashcima.geometry import Point, Transform, Vector2
from smashcima.scene import AffineSpace, LineGlyph


class LineSynthesizer(abc.ABC):
    """Interface for a line glyph synthesizer"""

    @abc.abstractmethod
    def supports_label(self, label: str) -> bool:
        """Returns true if the given glyph type can be synthesized.
        
        Override this when building custom line glyph synthesizers.
        """
        raise NotImplementedError

    def synthesize_line(
        self,
        label: str,
        parent_space: AffineSpace,
        start_point: Point,
        end_point: Point,
    ) -> LineGlyph:
        """Synthesizes a line with the given classification label and endpoints
        
        :param label: Which kind of line to synthesize (classification label)
        :param parent_space: The glyph will be placed into this space
        :param start_point: Where the line starts in the parent space
        :param end_point: Where the line ends in the parent space
        :returns: The newly synthesized glyph instance, already attached to
            the parent space.
        """
        # check that we are not accidentally passing in an Enum instead of str
        assert type(label) is str, "The requested glyph label is not a string"

        # compute the delta vector
        delta = end_point.vector - start_point.vector

        # create a new glyph
        glyph = self.create_glyph(
            label=label,
            delta=delta
        )

        # check its label
        assert glyph.label == label, f"The user requested class {label} " + \
            f"but got {glyph.label} instead"

        # compute the transform to apply to the created glyph to place
        # it exactly where the user wants it
        transform = LineSynthesizer.line_to_line_transform_preserving_thickness(
            from_origin=glyph.start_point.point,
            from_delta=(
                glyph.end_point.point.vector - glyph.start_point.point.vector
            ),
            to_origin=start_point,
            to_delta=delta
        )
        
        # attach the glyph to the parent space
        glyph.space.parent_space = parent_space
        glyph.space.transform = transform

        return glyph
    
    @staticmethod
    def line_to_line_transform_preserving_thickness(
        from_origin: Point,
        from_delta: Vector2,
        to_origin: Point,
        to_delta: Vector2
    ) -> Transform:
        """Computes transform mapping from one line segment to another.
        
        The segment thickness (the perpendicular direction) is preserved.

        :param from_origin: Starting point of the starting line segment.
        :param from_delta: Direction vector of the starting line segment.
        :param to_origin: Starting point of the target line segment.
        :param to_delta: Direction vector of the target line segment.
        """
        # frame is [origin, X unit, Y unit]
        from_frame = np.array([
            list(from_origin),
            list(from_origin.vector + from_delta),
            list(from_origin.vector + from_delta.normalize().rotate90degCC())
        ], dtype=np.float32)

        to_frame = np.array([
            list(to_origin),
            list(to_origin.vector + to_delta),
            list(to_origin.vector + to_delta.normalize().rotate90degCC())
        ], dtype=np.float32)

        matrix = cv2.getAffineTransform(from_frame, to_frame)

        return Transform(matrix)
    
    def create_glyph(self, label: str, delta: Vector2) -> LineGlyph:
        """Creates a new glyph instance of the specified label.

        The delta vector is used as a recommendation, not a command. It is
        the vector that the user wants to synthesize, but the created glyph
        will have its transform updated so that it matches the user's
        requested position and scale. But you can use this delta vector to
        create a glyph with the desired length / thickness / orientation.

        Override this method when building custom glyph synthesizers.
        The returned glyph should have no parent space.

        :param label: The kind of glyph to create.
        :param delta: Delta vector from the start point to the end point.
        """
        raise NotImplementedError
