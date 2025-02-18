from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List

from mung.node import Node

from smashcima.scene import Glyph


class MungDocument(ABC):
    """Encapsuales the code that parses one MuNG XML document.
    
    It provides helper methods for looking up Node links and such.
    """

    def __init__(
        self,
        path: Path,
        nodes: List[Node]
    ):
        self.path = path
        """Path to the MuNG XML file"""
        
        self.nodes = nodes
        """List of nodes as they are loaded by the mung library"""

        self.id_lookup: Dict[int, Node] = {
            c.id: c
            for c in self.nodes
        }
        """Dictionary for fast id lookup"""

        # self.point_cloud = PointCloud()
        # "Stores extracted points in crop objects"

    @abstractmethod
    def stamp_glyph(self, glyph: Glyph, node: Node):
        """Attaches MungGlyphMetadata object to the glyph"""
        raise NotImplementedError

    def get(self, node_id: int) -> Node:
        """Looks up a node by its integer ID"""
        return self.id_lookup[node_id]
    
    def get_outlink_to(self, node: Node, class_name: str) -> Node:
        """
        Returns the node at the end of any outlink
        with the given classname
        """
        for l in node.outlinks:
            resolved_link = self.get(l)
            if resolved_link.class_name == class_name:
                return resolved_link
        raise Exception("Node has no outlink of requested clsname")
    
    def get_inlink_from(self, node: Node, class_name: str) -> Node:
        """
        Returns the node at the end of any inlink
        with the given classname
        """
        for l in node.inlinks:
            resolved_link = self.get(l)
            if resolved_link.class_name == class_name:
                return resolved_link
        raise Exception("Node has no inlinks of requested clsname")

    def has_outlink_to(self, node: Node, class_name: str) -> bool:
        """
        Tests that there is a node at the end of any outlink
        with the given classname
        """
        for l in node.outlinks:
            resolved_link = self.get(l)
            if resolved_link.class_name == class_name:
                return True
        return False

    def has_inlink_from(self, node: Node, class_name: str) -> bool:
        """
        Tests that there is a node at the end of any inlink
        with the given classname
        """
        for l in node.inlinks:
            resolved_link = self.get(l)
            if resolved_link.class_name == class_name:
                return True
        return False
