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
        # We tested a few variants of extracting sprites from the dataset:
        # return _mask_defines_alpha(self.page_image, node)
        # return _lightness_defines_alpha_under_mask(self.page_image, node)
        return _binarized_adjusted_lightness(self.page_image, node)


def _mask_defines_alpha(page_image: np.ndarray, node: Node) -> np.ndarray:
    """Uses the mask to set the alpha channel, making the symbol look
    cropped out of the original image by the contours of the mask."""
    # crop out the image behind the node
    image_bgr = page_image[node.top:node.bottom, node.left:node.right, :]
    
    # define alpha channel by the mask
    image_alpha = node.mask * 255

    # combine BGR with the alpha channel
    return np.concatenate([image_bgr, image_alpha[:,:,np.newaxis]], axis=2)


def _lightness_defines_alpha_under_mask(
    page_image: np.ndarray,
    node: Node
) -> np.ndarray:
    """Uses the original image lightness as alpha value for the symbol,
    but only under the mask. Elsewhere sets alpha to zero. Makes symbols
    very translucent."""
    # crop out the image behind the node
    image_bgr = page_image[node.top:node.bottom, node.left:node.right, :]

    # use mask to determine the alpha channel
    alpha = node.mask * 255
    bitmap = np.concatenate([image_bgr, alpha[:,:,np.newaxis]], axis=2)

    # get lightness of the original image
    image_hls = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HLS)
    lightness = image_hls[:,:,1]

    # adjust alpha channel by lightness
    # (dark areas are less transparent)
    bitmap[:,:,3] = (255 - lightness) * node.mask

    return bitmap


def _binarized_adjusted_lightness(
    page_image: np.ndarray,
    node: Node
) -> np.ndarray:
    # crop out the image behind the node
    image_bgr = page_image[node.top:node.bottom, node.left:node.right, :]

    # get lightness of the original image
    image_hls = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HLS)
    lightness = image_hls[:,:,1]

    # apply Otsu binarization (blur creates two distinc modalities - ink&paper
    # and Otsu finds the midpoint between the two to use as the threshold)
    # also, use bilateral filter blur to preserve edges instead of gaussian
    blurred_lightness = cv2.bilateralFilter(lightness, 5, 25, 25)
    _, binarized = cv2.threshold(
        blurred_lightness, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # set everything outside the mask to white
    binarized[node.mask == 0] = 255

    # convert the black-on-white image to black-on-alpha
    bitmap = np.zeros(shape=(node.height, node.width, 4), dtype=np.uint8)
    bitmap[:,:,3] = 255 - binarized
    return bitmap

    # dummy preview (grayscale)
    # return np.stack([
    #     binarized, binarized, binarized, np.ones_like(lightness) * 255
    # ], axis=2)
