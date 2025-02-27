from typing import Dict

from mung.node import Node

from smashcima.geometry import Point


# names of points
ORIGIN_POINT = "origin" # for glyphs with a center
START_POINT = "start" # for line glyphs
END_POINT = "end" # for line glyphs


class PointSet:
    """Stores points for one MuNG node.
    Points are stored in the node's local 0-1 relative space, not pixels."""

    def __init__(self, node: Node):
        self.node = node
        """The MuNG node instance"""

        self.__points: Dict[str, Point] = dict()
        """The collection of points"""
    
    def __getitem__(self, name: str) -> Point:
        return self.__points[name]
    
    def __setitem__(self, name: str, point: Point):
        self.__points[name] = point
    
    def __delitem__(self, name: str):
        del self.__points[name]
    
    def __contains__(self, name: str) -> bool:
        return name in self.__points
    
    def get_in_relative_ratio(self, name: str) -> Point:
        """Returns a point, in the (default) relative-ratio space"""
        return self[name]
    
    def get_in_relative_pixels(self, name: str) -> Point:
        """Returns a point, transformed into the node-local pixel space"""
        p = self.get_in_relative_ratio(name)
        return Point(
            x=int(p.x * self.node.width),
            y=int(p.y * self.node.height)
        )
    
    def get_in_absolute_pixels(self, name: str) -> Point:
        """Returns a point, transformed into the page-global pixel space"""
        p = self.get_in_relative_ratio(name)
        return Point(
            x=int(self.node.left + p.x * self.node.width),
            y=int(self.node.top + p.y * self.node.height)
        )


class PointCloud:
    """
    Stores extracted points in a MuNG page, grouped by MuNG nodes.
    These points are retrieved later to get sprite origins and vector deltas.
    It stores up to one PointSet for each MuNG node.
    Points are stored in the node's local 0-1 relative space, not pixels.
    """

    def __init__(self) -> None:
        self.__sets_for_nodes: Dict[int, PointSet] = dict()
    
    def __getitem__(self, node: Node) -> PointSet:
        if node.id not in self.__sets_for_nodes:
            self.__sets_for_nodes[node.id] = PointSet(node)
        return self.__sets_for_nodes[node.id]
    
    def __delitem__(self, node: Node):
        del self.__sets_for_nodes[node.id]
    
    def __contains__(self, node: Node) -> bool:
        return node.id in self.__sets_for_nodes
