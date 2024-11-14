from dataclasses import dataclass
from typing import Optional

from smashcima.nameof_via_dummy import nameof_via_dummy
from smashcima.scene import Glyph, SceneObject

from .MppPage import MppPage


@dataclass
class MppGlyphMetadata(SceneObject):
    """Metadata information object for a glyph from the MUSCIMA++ dataset"""

    glyph: Glyph
    "The glyph that this metadata refers to"
    
    mpp_writer: int
    "Writer index (1 to 50) from the MUSCIMA++ dataset"

    mpp_piece: int
    "Music piece index (1 to 20) from the MUSCIMA++ dataset"

    mpp_numeric_objid: int
    "Id number assigned to the corresponding crop object in the MUSCIMA++ dataset"

    def __post_init__(self):
        assert self.glyph is not None
        assert self.mpp_writer is not None
        assert self.mpp_writer >= 1 and self.mpp_writer <= 50
        assert self.mpp_piece is not None
        assert self.mpp_piece >= 1 and self.mpp_piece <= 20
    
    @property
    def mpp_crop_object_uid(self) -> str:
        """The full XML id of the corresponding crop object"""
        assert self.mpp_numeric_objid is not None
        w = str(self.mpp_writer).zfill(2)
        n = str(self.mpp_piece).zfill(2)
        i = str(self.mpp_numeric_objid)
        return f"MUSCIMA-pp_1.0___CVC-MUSCIMA_W-{w}_N-{n}_D-ideal___{i}"

    @staticmethod
    def stamp_glyph(glyph: Glyph, mpp_page: MppPage, numeric_objid: int):
        # just create an instance and that's it
        # the glyph's inlinks will hold on to the instance
        MppGlyphMetadata(
            glyph=glyph,
            mpp_writer=mpp_page.mpp_writer,
            mpp_piece=mpp_page.mpp_piece,
            mpp_numeric_objid=numeric_objid
        )
    
    @staticmethod
    def of_glyph(
        glyph: Glyph,
        fail_if_none=False
    ) -> Optional["MppGlyphMetadata"] | "MppGlyphMetadata":
        return glyph.get_inlinked(
            MppGlyphMetadata,
            nameof_via_dummy(MppGlyphMetadata, lambda m: m.glyph),
            at_most_one=True,
            fail_if_none=fail_if_none
        )
