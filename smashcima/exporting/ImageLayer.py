from dataclasses import dataclass
from typing import List

import numpy as np

from smashcima.scene import AffineSpace, LabeledRegion


@dataclass
class ImageLayer:
    """Represents a layer of image data in the compositor.

    It is the primary data-object in the compositor. It holds the pixel-level
    information as well as the geometric information (keypoints, regions,
    bounding boxes). It is designed in a way to be passable through
    typical image-augmentation libraries, such as Albumentation or Augraphy.
    """
    
    bitmap: np.ndarray
    """The BGRA pixel-level image data for this layer"""

    dpi: float
    """DPI of the image"""

    space: AffineSpace
    """The (root) affine space that aligns with pixel-coordinates.
    It is needed for the other geometric objects to have a parent.
    All geometric objects are direct children of this space,
    there is no hierarchy."""

    regions: List[LabeledRegion]
    """All the 'masks' in the image layer. Smashcima does not support
    rasterized masks, instead all masks are vectorized and represented
    by these region objects. Regions have their original classification
    labels and can undergo geometric transformations as sets of points.
    Therefore bounding boxes (and raster masks) can be extracted from
    them later. In non-affine transformation, the region may get distorted
    (since it's treated only as a set of points). If you implement an
    augmentation that performs heavy non-affine distortion and want the
    resulting region to be accurate, you need to subdivide the region to
    increase its resolution."""

    # NOTE: scene points / keypoints can be added here later

    def __post_init__(self):
        # same conditions as in the Sprite class
        assert len(self.bitmap.shape) == 3 # [H, W, C]
        assert self.bitmap.shape[2] == 4 # BGRA
        assert self.bitmap.dtype == np.uint8
        assert self.bitmap.shape[0] > 0 and self.bitmap.shape[1] > 0

        # verify that all regions belong to the root affine space
        assert all(r.space is self.space for r in self.regions)
    
    @property
    def width(self) -> int:
        """Width of the image layer in pixels"""
        return self.bitmap.shape[1]

    @property
    def height(self) -> int:
        """Height of the image layer in pixels"""
        return self.bitmap.shape[0]
