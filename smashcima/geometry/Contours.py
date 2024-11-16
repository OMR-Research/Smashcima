from typing import List, Sequence

import numpy as np

from .Polygon import Polygon
from .Rectangle import Rectangle


class Contours:
    """Contours is a list of polygons that together encapsulate a shape"""

    def __init__(self, polygons: List[Polygon]):
        self.polygons = polygons

    @staticmethod
    def from_cv2_contours(cv_contours: Sequence[np.ndarray]) -> "Contours":
        """Constructs a polygon from an OpenCV contour instance"""
        return Contours([
            Polygon.from_cv2_contour(cv_contour)
            for cv_contour in cv_contours
        ])

    def bbox(self) -> Rectangle:
        """Returns the bounding box of all contours"""
        point_cloud = [
            point for polygon in self.polygons for point in polygon.points
        ]
        return Polygon(point_cloud).bbox()
