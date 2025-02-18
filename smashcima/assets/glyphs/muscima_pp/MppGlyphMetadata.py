from dataclasses import dataclass
from typing import Optional

from ..mung.MungGlyphMetadata import MungGlyphMetadata
from smashcima.scene import Glyph

from .MppPage import MppPage


@dataclass
class MppGlyphMetadata(MungGlyphMetadata):
    """Metadata information object for a glyph from the MUSCIMA++ dataset"""

    @property
    def mpp_writer(self) -> int:
        """Writer index (1 to 50) from the MUSCIMA++ dataset"""
        return int(self.mung_style)

    mpp_piece: int
    """Music piece index (1 to 20) from the MUSCIMA++ dataset"""

    @property
    def mpp_numeric_objid(self) -> int:
        """Id number assigned to the corresponding crop object in
        the MUSCIMA++ dataset"""
        return self.mung_node_id

    def __post_init__(self):
        super().__post_init__()
        assert self.mpp_writer >= 1 and self.mpp_writer <= 50
        assert self.mpp_piece >= 1 and self.mpp_piece <= 20
    
    @property
    def mpp_crop_object_uid(self) -> str:
        """The full XML id of the corresponding crop object"""
        # e.g. "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-01_N-01_D-ideal___351"
        i = str(self.mung_node_id)
        return f"MUSCIMA-pp_1.0___{self.mung_document}___{i}"

    @staticmethod
    def stamp_glyph(glyph: Glyph, mpp_page: MppPage, numeric_objid: int):
        w = str(mpp_page.mpp_writer).zfill(2)
        n = str(mpp_page.mpp_piece).zfill(2)

        # just create an instance and that's it
        # the glyph's inlinks will hold on to the instance
        MppGlyphMetadata(
            glyph=glyph,
            mung_style=str(mpp_page.mpp_writer),
            mung_document=f"CVC-MUSCIMA_W-{w}_N-{n}_D-ideal",
            mung_node_id=numeric_objid,
            mpp_piece=mpp_page.mpp_piece
        )
    
    @classmethod
    def of_glyph(cls, glyph: Glyph):
        return cls.of(glyph, lambda m: m.glyph)

    @classmethod
    def of_glyph_or_none(cls, glyph: Optional[Glyph]):
        return cls.of_or_none(glyph, lambda m: m.glyph)
