import numpy as np

from .SceneObject import SceneObject
from .AffineSpace import AffineSpace
from ..geometry.Vector2 import Vector2
from ..geometry.Transform import Transform
from ..geometry.Point import Point
from ..geometry.Rectangle import Rectangle
from ..geometry.units import px_to_mm, mm_to_px


class Sprite(SceneObject):
    """Sprite is a bitmap image within the scene hierarchy"""
    
    def __init__(
        self,
        space: AffineSpace,
        bitmap: np.ndarray,
        bitmap_origin: Point = Point(0.5, 0.5),
        dpi: float = 300,
        transform: Transform = Transform.identity()
    ):
        super().__init__()

        self.space = space
        "What parent space does the sprite exist in"

        self.transform = transform
        """Transform that places the sprite within the parent space - the origin
        of the transform will become the origin of the bitmap."""

        assert len(bitmap.shape) == 3 # [H, W, C]
        assert bitmap.shape[2] == 4 # BGRA
        assert bitmap.dtype == np.uint8
        self.bitmap = bitmap
        "The numpy opencv BGRA bitmap for the sprite"

        self.bitmap_origin = bitmap_origin
        """Origin point of the sprite in the normalized pixel space (0.0 - 1.0),
        that is, where does the sprite overlap with the scene object's origin"""

        self.dpi = float(dpi)
        """What is the DPI of the sprite image, another words, how to scale
        the sprite - how to determine the scene size in millimeters,
        when we have the size in pixels"""
    
    @property
    def pixel_width(self) -> int:
        return self.bitmap.shape[1]
    
    @property
    def pixel_height(self) -> int:
        return self.bitmap.shape[0]
    
    @property
    def physical_width(self) -> float:
        return px_to_mm(self.pixel_width, dpi=self.dpi)
    
    @property
    def physical_height(self) -> float:
        return px_to_mm(self.pixel_height, dpi=self.dpi)
    
    @property
    def pixels_bbox(self) -> Rectangle:
        """Returns the bounding box rectangle of the sprite in its pixel
        space - that is (0, 0, px_width, px_height)"""
        return Rectangle(0, 0, self.pixel_width, self.pixel_height)
    
    @classmethod
    def many_of_space(cls, space: AffineSpace):
        return cls.many_of(space, lambda s: s.space)
    
    def get_pixels_to_scene_transform(self) -> Transform:
        """Returns a transform that converts from local pixel space
        to local scene space (excluding the sprite transform property)"""
        return (
            Transform.translate(Vector2(
                -self.bitmap_origin.x * self.pixel_width,
                -self.bitmap_origin.y * self.pixel_height
            ))
            .then(Transform.scale(px_to_mm(1, dpi=self.dpi)))
        )
    
    def detach(self):
        """Detaches the sprite from the scene hierarchy"""
        self.space = None

    @staticmethod
    def debug_box(
        space: AffineSpace,
        rectangle: Rectangle,
        fill_color = (0, 0, 255, 64), # BGRA
        border_color = (0, 0, 255, 255), # BGRA
        border_width: float = 1,
        dpi: float = 300
    ) -> "Sprite":
        """Creates a rectangular box image sprite with the desired properties"""
        pixel_width = int(mm_to_px(rectangle.width, dpi=dpi))
        pixel_height = int(mm_to_px(rectangle.height, dpi=dpi))
        border_width_px = int(round(mm_to_px(border_width, dpi=dpi)))

        # border is at least 1 px if width is non-zero
        if border_width > 0 and border_width_px == 0:
            border_width_px = 1

        bitmap = np.zeros(
            shape=(pixel_height, pixel_width, 4),
            dtype=np.uint8
        )

        # paint fill
        bitmap[:,:] = fill_color

        # paint border
        if border_width_px > 0:
            bitmap[:border_width_px, :] = border_color
            bitmap[-border_width_px:, :] = border_color
            bitmap[:, :border_width_px] = border_color
            bitmap[:, -border_width_px:] = border_color

        # create the sprite instance
        sprite = Sprite(
            space=space,
            bitmap=bitmap,
            bitmap_origin=Point(0.5, 0.5),
            dpi=dpi
        )
        sprite.transform = Transform.translate(rectangle.center.vector)
        return sprite

    @staticmethod
    def rectangle(
        space: AffineSpace,
        rectangle: Rectangle,
        fill_color = (0, 0, 255, 64), # BGRA
        dpi: float = 300
    ) -> "Sprite":
        """Creates a rectangle filled with the given color at a given DPI"""
        pixel_width = int(mm_to_px(rectangle.width, dpi=dpi))
        pixel_height = int(mm_to_px(rectangle.height, dpi=dpi))
        
        bitmap = np.zeros(
            shape=(pixel_height, pixel_width, 4),
            dtype=np.uint8
        )

        # paint fill
        bitmap[:,:] = fill_color

        # create the sprite instance
        sprite = Sprite(
            space=space,
            bitmap=bitmap,
            bitmap_origin=Point(0.5, 0.5),
            dpi=dpi
        )
        sprite.transform = Transform.translate(rectangle.center.vector)
        return sprite
