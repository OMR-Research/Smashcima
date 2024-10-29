from pathlib import Path
from muscima.io import parse_cropobject_list, CropObject
from typing import List, Dict
from .PointCloud import PointCloud
import re


class MppPage:
    """
    The CVC-MUSCIMA dataset consists of 1000 scanned pages.
    This class represents one of them, annotated according to the MUSCIMA++
    standard. (Note: MUSCIMA++ contains only 140 pages out of the 1000)
    """
    def __init__(
        self,
        crop_objects: List[CropObject],
        mpp_writer: int,
        mpp_piece: int
    ):
        self.crop_objects = crop_objects
        "List of cropobjects as they are loaded by the muscima library"

        self.id_lookup: Dict[int, CropObject] = {
            c.objid: c
            for c in self.crop_objects
        }
        "Dictionary for fast id lookup"

        self.point_cloud = PointCloud()
        "Stores extracted points in crop objects"

        assert mpp_writer >= 1 and mpp_writer <= 50
        self.mpp_writer = mpp_writer
        "Writer index (1 to 50) from the MUSCIMA++ dataset"

        assert mpp_piece >= 1 and mpp_piece <= 20
        self.mpp_piece = mpp_piece
        "Music piece index (1 to 20) from the MUSCIMA++ dataset"

    @staticmethod
    def load(path: Path) -> "MppPage":
        crop_objects: List[CropObject] = parse_cropobject_list(path)

        m = re.match(r"CVC-MUSCIMA_W-(\d+)_N-(\d+)_D-ideal", path.stem)
        mpp_writer = int(m.group(1))
        mpp_piece = int(m.group(2))

        return MppPage(crop_objects, mpp_writer, mpp_piece)
    
    def get(self, objid: int) -> CropObject:
        """Looks up a crop object by its integer ID"""
        return self.id_lookup[objid]
    
    def get_outlink_to(self, obj: CropObject, clsname: str) -> CropObject:
        """
        Returns the crop object at the end of any outlink
        with the given classname
        """
        for l in obj.outlinks:
            resolved_link = self.get(l)
            if resolved_link.clsname == clsname:
                return resolved_link
        raise Exception("Object has no outlink of requested clsname")
    
    def get_inlink_from(self, obj: CropObject, clsname: str) -> CropObject:
        """
        Returns the crop object at the end of any inlink
        with the given classname
        """
        for l in obj.inlinks:
            resolved_link = self.get(l)
            if resolved_link.clsname == clsname:
                return resolved_link
        raise Exception("Object has no inlinks of requested clsname")

    def has_outlink_to(self, obj: CropObject, clsname: str) -> bool:
        """
        Tests that there is a crop object at the end of any outlink
        with the given classname
        """
        for l in obj.outlinks:
            resolved_link = self.get(l)
            if resolved_link.clsname == clsname:
                return True
        return False

    def has_inlink_from(self, obj: CropObject, clsname: str) -> bool:
        """
        Tests that there is a crop object at the end of any inlink
        with the given classname
        """
        for l in obj.inlinks:
            resolved_link = self.get(l)
            if resolved_link.clsname == clsname:
                return True
        return False
