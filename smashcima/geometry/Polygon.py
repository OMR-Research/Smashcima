from .Point import Point
from .Rectangle import Rectangle
from .Quad import Quad
from typing import List
import numpy as np


class Polygon:
    """
    Polygon is a list of points that enclose an area.
    """

    def __init__(self, points: List[Point]):
        self.points = points

    @staticmethod
    def from_rectangle(rectangle: Rectangle) -> "Polygon":
        """Constructs a polygon from a rectangle by going over its corners
        from top left, in the clocwise direction."""
        return Polygon([
            rectangle.top_left_corner,
            rectangle.top_right_corner,
            rectangle.bottom_right_corner,
            rectangle.bottom_left_corner
        ])

    @staticmethod
    def from_quad(quad: Quad) -> "Polygon":
        """Constructs a polygon from a quad."""
        return Polygon([quad.a, quad.b, quad.c, quad.d])

    @staticmethod
    def from_cv2_contour(contour: np.ndarray) -> "Polygon":
        """Constructs a polygon from an OpenCV contour instance"""
        # enumerated points are vertical vectors: [[X, Y]]
        return Polygon([Point(p[0, 0], p[0, 1]) for p in contour])

    def __repr__(self):
        return f"Quad({self.a}, {self.b}, {self.c}, {self.d})"

    def bbox(self) -> Rectangle:
        """Returns the bounding box of the polygon"""
        pts = self.points
        top = min(p.y for p in pts)
        bottom = max(p.y for p in pts)
        left = min(p.x for p in pts)
        right = max(p.x for p in pts)
        return Rectangle(
            x=left,
            y=top,
            width=right-left,
            height=bottom-top
        )
