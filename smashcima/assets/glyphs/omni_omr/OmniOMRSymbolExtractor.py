import cv2
import numpy as np
from mung.node import Node

from smashcima.scene import Glyph

from ..mung.extraction.ExtractedBag import ExtractedBag
from ..mung.extraction.MungDocument import MungDocument
from ..mung.extraction.MungSymbolExtractor import MungSymbolExtractor
from .OmniOMRGlyphMetadata import OmniOMRGlyphMetadata


class OmniOMRSymbolExtractor(MungSymbolExtractor):
    def __init__(self, document: MungDocument, bag: ExtractedBag) -> None:
        super().__init__(document, bag)

        # extract metadata
        parts = self.document.path.stem.split("_")
        assert len(parts) == 2
        self.mzk_book_uuid: str = parts[0]
        self.mzk_page_uuid: str = parts[1]

        # extract path to the image and load it
        image_path = (self.document.path.parent.parent
                      / "images" / self.document.path.stem)
        self.page_image = cv2.imread(str(image_path), cv2.IMREAD_COLOR_BGR)
        """Page image in the BGR format"""


    def stamp_glyph(self, glyph: Glyph, node: Node):
        OmniOMRGlyphMetadata.stamp_glyph(
            glyph=glyph,
            node=node,
            mzk_book_uuid=self.mzk_book_uuid,
            mzk_page_uuid=self.mzk_page_uuid
        )
    
    def sprite_bitmap_from_mung_node(self, node: Node) -> np.ndarray:
        # crop out the image behind the node
        image_bgr = self.page_image[
            node.top:node.bottom,
            node.left:node.right,
            :
        ]

        # use mask to determine the alpha channel
        alpha = node.mask * 255
        bitmap = np.concatenate([image_bgr, alpha[:,:,np.newaxis]], axis=2)

        # get lightness of the original image
        # image_hls = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HLS)
        # lightness = image_hls[:,:,1]

        # adjust alpha channel by lightness
        # (dark areas are less transparent)
        # bitmap[:,:,3] = (255 - lightness) * node.mask

        return bitmap
