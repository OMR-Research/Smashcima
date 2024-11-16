from typing import TypeVar

import cv2
import numpy as np

from .Contours import Contours
from .Point import Point
from .Polygon import Polygon
from .Quad import Quad
from .Vector2 import Vector2

T = TypeVar("T")


class Transform:
    """
    2D affine transform.

    When used in scene objects, it maps from the local space
    to the parent object's space.
    """

    # Based on:
    # https://www.w3.org/TR/SVGTiny12/coords.html#TransformAttribute

    def __init__(self, matrix: np.ndarray):
        assert matrix.shape == (2, 3)
        assert matrix.dtype == np.float64
        
        self.matrix = matrix
        "The 2x3 transformation matrix as a numpy array"

    @property
    def matrix3(self) -> np.ndarray:
        """The 3x3 extended matrix of this transformation"""
        return np.concatenate(
            (self.matrix, np.array([[0, 0, 1]], dtype=np.float64)),
            axis=0
        )

    @property
    def matrix2(self) -> np.ndarray:
        """The 2x2 matrix that ignores translation"""
        return self.matrix[0:2, 0:2]

    @property
    def determinant(self) -> float:
        """Returns the determinant of the affine transformation"""
        return np.linalg.det(self.matrix2)

    def inverse(self) -> "Transform":
        """Returns the inverted affine transform"""
        return Transform(cv2.invertAffineTransform(self.matrix))

    def apply_to(self, other: T) -> T:
        """Transform a vector or another transformation"""
        m = self.matrix3
        if isinstance(other, Transform):
            o = other.matrix3
            r = m.dot(o)
            return Transform(r[0:2, :]) # type: ignore
        elif isinstance(other, Vector2):
            o = np.array([[other.x], [other.y], [1]], dtype=np.float64)
            r = m.dot(o)
            return Vector2(r[0, 0], r[1, 0]) # type: ignore
        elif isinstance(other, Point):
            v = self.apply_to(other.vector)
            return Point(v.x, v.y) # type: ignore
        elif isinstance(other, Quad):
            pts = [self.apply_to(p) for p in other.points]
            return Quad(*pts) # type: ignore
        elif isinstance(other, Polygon):
            pts = [self.apply_to(p) for p in other.points]
            return Polygon(pts) # type: ignore
        elif isinstance(other, Contours):
            ps = [self.apply_to(p) for p in other.polygons]
            return Contours(ps) # type: ignore
        else:
            raise ValueError(
                "Transform applied to an unexpected type: " +
                str(type(other))
            )

    def __matmul__(self, other: T) -> T:
        return self.apply_to(other)

    def then(self, other: "Transform") -> "Transform":
        """
        Lets you chain transformations, thereby defining a new transformation.
        This method practically just inverts the matmul multiplication order
        to be chronological in terms of going from local spaces up towards
        the global scene space.
        """
        return other @ self

    @staticmethod
    def identity() -> "Transform":
        """Returns the identity transform"""
        return Transform(
            np.array([
                [1, 0, 0],
                [0, 1, 0]
            ], dtype=np.float64)
        )

    @staticmethod
    def translate(offset: Vector2) -> "Transform":
        """Returns a translation transform"""
        return Transform(
            np.array([
                [1, 0, offset.x],
                [0, 1, offset.y]
            ], dtype=np.float64)
        )

    @staticmethod
    def scale(scale: float) -> "Transform":
        """Returns a scaling transform"""
        return Transform(
            np.array([
                [scale, 0, 0],
                [0, scale, 0]
            ], dtype=np.float64)
        )

    @staticmethod
    def rotateDegCC(angle: float):
        """Creates a rotation transform for a coutner-clockwise rotation
        of a given number of degrees"""
        matrix = cv2.getRotationMatrix2D((0, 0), angle, 1)
        return Transform(matrix)
