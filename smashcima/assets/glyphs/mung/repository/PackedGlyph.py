import pickle

from smashcima.scene import Glyph

from ..MungGlyphMetadata import MungGlyphMetadata


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
        label: str,
        mung_style: str,
        data: bytes
    ):
        self.label = label
        """Glyph classification label"""
        
        self.mung_style = mung_style
        """Style identifier of the mung glyph (writer number, book UUID, ...)"""

        self.data = data
        """The pickled glyph instance"""

    @staticmethod
    def pack_glyph(glyph: Glyph) -> "PackedGlyph":
        return PackedGlyph(
            label=glyph.label,
            mung_style=MungGlyphMetadata.of_glyph(glyph).mung_style,
            data=pickle.dumps(glyph)
        )
    
    def unpack(self) -> Glyph:
        return pickle.loads(self.data)
