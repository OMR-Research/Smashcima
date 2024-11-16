import pickle
from typing import Optional

from smashcima.scene import Glyph, LineGlyph

from .MppGlyphMetadata import MppGlyphMetadata


class PackedGlyph:
    """Contains a sub-pickled glyph so that the loading of the whole repository
    is much faster. The glyph is unpacked only once sampled and needed.
    
    This is because creating python objects takes most of the time,
    so this approach reduces the number of python objects created when the
    symbol repository is unpickled from the file system.

    This trick speeds up loading the repository pickle file from about
    15 seconds down to under a second.
    """
    
    def __init__(
        self,
        line_length: Optional[float],
        mpp_writer: int,
        data: bytes
    ):
        self.line_length = line_length
        """If a line glyph, stores its length for sampling lookups"""
        
        self.mpp_writer = mpp_writer
        """Number of the MUSCIMA++ writer"""

        self.data = data
        """The pickled glyph instance"""

    @staticmethod
    def pack(glyph: Glyph) -> "PackedGlyph":
        line_length: Optional[float] = None
        if isinstance(glyph, LineGlyph):
            line_length = glyph.line_length
        return PackedGlyph(
            line_length=line_length,
            mpp_writer=MppGlyphMetadata.of_glyph(glyph).mpp_writer,
            data=pickle.dumps(glyph)
        )
    
    def unpack(self) -> Glyph:
        return pickle.loads(self.data)
