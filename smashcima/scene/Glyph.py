from dataclasses import dataclass
from typing import List

import cv2
import numpy as np

from smashcima.geometry import Contours, Point, Polygon, Rectangle

from .AffineSpace import AffineSpace
from .LabeledRegion import LabeledRegion
from .SceneObject import SceneObject
from .ScenePoint import ScenePoint
from .Sprite import Sprite


@dataclass
class Glyph(SceneObject):
    """Set of sprites together with their label and segmentation region.

    A glyph is a visual unit of the notation. It can be detected, segmented,
    classified.

    It is: notehead, stem, flag, leger line, staffline,
    But it's also: notehead-stem-flag ligature, leger-notehead-stem ligature
    Since a ligature cannot be easily broken down into its parts,
    it's a glyph of its own.

    The glyph has its own local coordinate space, relative to which all spatial
    information is represented.

    Also, see the definition of a glyph:
    https://en.wikipedia.org/wiki/Glyph
    """

    space: AffineSpace
    """Space in which glyph components live. The origin is usually well
    defined for each glyph label. The space instance is owned by this
    Glyph instance - should be created, moved, and deleted together."""

    region: LabeledRegion
    """The segmentation mask region, defines the label and bounding box"""

    sprites: List[Sprite]
    """Sprites that make up the visual appearance of the glyph"""

    @property
    def label(self) -> str:
        """Label used for object classification, identifies the type of glyph"""
        return self.region.label
    
    @label.setter
    def label(self, value: str) -> None:
        self.region.label = value
    
    def detach(self):
        """Unlink the glyph from the scene"""
        self.space.parent_space = None # the important bit
        self.region = None
        self.sprites = []
    
    @staticmethod
    def build_region_from_sprites_alpha_channel(
        label: str,
        sprites: List[Sprite],
        threshold: float = 0.5
    ) -> LabeledRegion:
        """Constructs a labeled region from a set of sprites by their alpha.

        All the sprites must already be attached to the same affine space
        and this space will be used as the space of the constructed region.

        This method does not assume overlap in sprites. If resulting contours
        overlap, they will stay overlapping in the resulting region and no
        morphological union will be performed.

        :param label: The classification label that will be assigned to
            the region
        :param sprites: Sprites to use to region construction
        :param threshold: Threshold to use for alpha channel binarization,
            float in 0.0 - 1.0 range.
        """
        assert len(sprites) > 0, "You must provide at least one sprite"

        # get the affine space
        space = sprites[0].space
        assert space is not None, "All provided sprites must have space set"
        assert all(s.space is space for s in sprites), \
            "All provided sprites must be in the same affine space"
        
        contour_polygons: List[Polygon] = []

        # for each sprite
        for sprite in sprites:

            # run contour extraction
            mask = sprite.bitmap[:, :, 3] >= int(threshold * 255)
            img = np.zeros(shape=mask.shape, dtype=np.uint8)
            img[mask] = 255
            cv_contours, _ = cv2.findContours(
                img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
            )

            # wrap the results in geometry instances
            transform = sprite.get_pixels_to_origin_space_transform()\
                .then(sprite.transform)
            for cv_contour in cv_contours:
                polygon = transform.apply_to(
                    Polygon.from_cv2_contour(cv_contour)
                )
                contour_polygons.append(polygon)
        
        # build the final region instance
        return LabeledRegion(
            space=space,
            contours=Contours(contour_polygons),
            label=label
        )
    
    def get_bbox_in_space(self, target_space: AffineSpace) -> Rectangle:
        """Returns the bounding box rectangle in the target space coordinates
        
        :param target_space: The space to which coordinates of the contours
            should be transformed. Must be an ancestor of this glyph's space.
        """
        return self.region.get_bbox_in_space(target_space)

    def place_debug_overlay(self) -> List[Sprite]:
        """Places sprites that act as debugging overlay for the glyph.
        Override this method to add more overlay for specialized glyphs."""
        overlay: List[Sprite] = []

        # green origin point
        p = ScenePoint(
            point=Point(0, 0),
            space=self.space
        )
        overlay.append(
            p.place_debug_overlay(color=(0, 255, 0, 128))
        )
        p.detach()
        del p

        return overlay
