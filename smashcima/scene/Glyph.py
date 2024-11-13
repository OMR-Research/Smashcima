from dataclasses import dataclass, field
from .SceneObject import SceneObject
from .Sprite import Sprite
from .AffineSpace import AffineSpace
from .ScenePoint import ScenePoint
from smashcima.geometry.Polygon import Polygon
from smashcima.geometry.Rectangle import Rectangle
from smashcima.geometry.Point import Point
from typing import List
import numpy as np
import cv2


@dataclass
class Glyph(SceneObject):
    """
    A glyph is a visual unit of the notation. It can be detected, segmented,
    classified.

    It is: notehead, stem, flag, ledger line, staffline,
    But it's also: notehead-stem-flag ligature, ledger-notehead-stem ligature
    Since a ligature cannot be easily broken down into its parts,
    it's a glyph of its own.

    The glyph has its own local coordinate space, relative to which all spatial
    information is represented.

    Also, see the definition of a glyph:
    https://en.wikipedia.org/wiki/Glyph
    """

    glyph_class: str
    "Class name used for classification"

    space: AffineSpace = field(default_factory=AffineSpace)
    """The local space of the glyph, where the origin point is some important
    point of the glyph (depends on the glyph class, e.g. center of a notehead
    or the base of a stem)"""

    sprites: List[Sprite] = field(default_factory=list)
    "Images that should be rendered for the glyph."

    def __post_init__(self):
        assert type(self.glyph_class) is str, "Glyph class must be string"
    
    def detach(self):
        """Unlink the glyph from the scene"""
        self.space.parent_space = None
    
    def get_segmentation_mask_of_sprite(self, sprite: Sprite) -> np.ndarray:
        """Given a sprite in this glyph, returns its segmentation mask
        (a 2D array of booleans for the sprite bitmap). Override this
        method to control the semantic segmentation output for the glyph."""
        assert sprite in self.sprites, "Given sprite must belong to this glyph"

        # default behaviour: 0.5-thresholded alfa channel
        return sprite.bitmap[:, :, 3] >= 0.5
    
    def get_contours(self) -> List[Polygon]:
        """Returns the list of countours of the glyph, using the segmentation
        mask. The polygon lives in the glyph affine space. Override this method
        to control the countours for the glyph."""
        out_contours: List[Polygon] = []

        # NOTE: this algorithm assumes no overlap between individual sprites
        
        # for each sprite
        for sprite in self.sprites:

            # run contour extraction
            mask = self.get_segmentation_mask_of_sprite(sprite)
            img = np.zeros(shape=mask.shape, dtype=np.uint8)
            img[mask] = 255
            cv_contours, _ = cv2.findContours(
                img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
            )

            # wrap the results in geometry instances
            transform = sprite.get_pixels_to_scene_transform()\
                .then(sprite.transform)
            for cv_contour in cv_contours:
                out_contour = transform.apply_to(
                    Polygon.from_cv2_contour(cv_contour)
                )
                out_contours.append(out_contour)

        return out_contours
    
    def get_bbox_in_space(self, space: AffineSpace) -> Rectangle:
        """Returns the bounding box of this glyph in the given affine space"""
        transform = space.transform_from(self.space)
        contours = self.get_contours()
        point_cloud = Polygon([p for c in contours for p in c.points])
        point_cloud_transformed = transform.apply_to(point_cloud)
        return point_cloud_transformed.bbox()

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
