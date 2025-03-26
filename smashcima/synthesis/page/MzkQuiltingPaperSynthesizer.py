from smashcima.scene.AffineSpace import AffineSpace
from smashcima.scene.Sprite import Sprite
from smashcima.geometry.Rectangle import Rectangle
from smashcima.geometry.Transform import Transform
from smashcima.geometry.Point import Point
from smashcima.geometry.Vector2 import Vector2
from ..PaperSynthesizer import PaperSynthesizer
from ..style.MzkPaperStyleDomain import MzkPaperStyleDomain
from smashcima.assets.AssetRepository import AssetRepository
from smashcima.assets.textures.MzkPaperPatches import MzkPaperPatches
from smashcima.geometry.units import mm_to_px
from .Quilter import Quilter
import numpy as np
import random
import cv2


class MzkQuiltingPaperSynthesizer(PaperSynthesizer):
    def __init__(
        self,
        assets: AssetRepository,
        style_domain: MzkPaperStyleDomain,
        rng: random.Random
    ):
        self.bundle = assets.resolve_bundle(MzkPaperPatches)
        self.style_domain = style_domain
        self.quilter = Quilter(rng)

    def synthesize_paper(
        self,
        page_space: AffineSpace,
        placement: Rectangle
    ):
        patch = self.style_domain.current_patch
        source_texture = self.bundle.load_bitmap_for_patch(patch)

        # TODO: smooth out any brightness changes over the source texture
        # (more likely this should be part of the asset bundle, not here)
        
        quilted_texture = self.quilter.quilt_texture_to_dimensions(
            source_texture=source_texture,
            target_width_px=int(mm_to_px(placement.width, patch.dpi)),
            target_height_px=int(mm_to_px(placement.height, patch.dpi)),
        )

        # create the sprite scene object
        Sprite(
            space=page_space,
            bitmap=quilted_texture,
            bitmap_origin=Point(0, 0),
            dpi=patch.dpi,
            transform=Transform.translate(Vector2(placement.x, placement.y))
        )
