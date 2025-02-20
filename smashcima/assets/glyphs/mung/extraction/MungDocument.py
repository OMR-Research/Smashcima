from pathlib import Path
from typing import List

from mung.io import read_nodes_from_file
from mung.node import Node
from mung.graph import NotationGraph


class MungDocument:
    """Represents one MuNG XML document.
    
    It is given to the symbol extractor as input.
    """

    def __init__(
        self,
        path: Path,
        nodes: List[Node],
        dpi: float
    ):
        self.path = path
        """Path to the MuNG XML file"""

        self.graph = NotationGraph(nodes)
        """The notation graph for the MuNG document"""
        
        self.dpi = dpi
        """DPI of the original image that MuNG describes"""
    
    @staticmethod
    def load(path: Path, dpi: float) -> "MungDocument":
        nodes: List[Node] = read_nodes_from_file(str(path))
        return MungDocument(
            path=path,
            nodes=nodes,
            dpi=dpi
        )
