from typing import Dict, List
from smashcima.geometry.Point import Point
from muscima.io import CropObject


class PointCloud:
    """
    Stores detected points in MUSCIMA++ crop objects for one annotated page.
    These points can then be retrieved later when finding origins and
    placement distributions.

    It's a map from objid to a list of points in the mask pixel coordinates.
    """

    def __init__(self):
        self._map: Dict[int, List[Point]] = dict()
    
    def set_points(self, o: CropObject, points: List[Point]):
        self._map[o.objid] = list(points)
    
    def get_points(self, o: CropObject) -> List[Point]:
        if o.objid not in self._map:
            raise KeyError("There are no points for object " + str(o.uid))
        return self._map[o.objid]
