from typing import List, Tuple

import numpy as np

from smashcima.geometry import (Point, Rectangle, Transform, Vector2, mm_to_px,
                                px_to_mm)

from .AffineSpace import AffineSpace
from .AffineSpaceVisitor import AffineSpaceVisitor
from .SceneObject import SceneObject


class Sprite(SceneObject):
    """A bitmap image embedded inside the affine space hierarchy
    
    The bitmap is an OpenCV numpy array with BGRA channels and uint8 type.
    
    The sprite lives its parent affine space. The sprite's transform determines,
    where in the affine space lands the bitmap origin point (and possibly
    its orientation and scale). The bitmap origin then specifies, where in the
    bitmap (0.0 to 1.0) is the origin located and the DPI specifies the size
    of a pixel, which in turn defines the physical size of the sprite.

    Another words, a Sprite is a bitmap, with positioning and scaling
    information provided. Scaling is determined by DPI and the origin and
    transform determine the positioning. (Transforms may modify scale in theory,
    but it's a convention that all affine space transforms preserve scale)
    """
    
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
        """The affine space in which the sprite is embedded"""

        self.transform = transform
        """Transform that maps the origin space into the parent space"""

        assert len(bitmap.shape) == 3 # [H, W, C]
        assert bitmap.shape[2] == 4 # BGRA
        assert bitmap.dtype == np.uint8
        assert bitmap.shape[0] > 0 and bitmap.shape[1] > 0
        self.bitmap = bitmap
        """The numpy opencv BGRA bitmap for the sprite"""

        self.bitmap_origin = bitmap_origin
        """Origin point of the sprite in the normalized pixel space (0.0 - 1.0),
        that is, where does the bitmap overlap with the sprite's transform
        origin"""

        self.dpi = float(dpi)
        """DPI of the bitmap, used for conversion between px and millimeters.
        Together with bitmap resolution determines the sprite's physical size"""
    
    @property
    def pixel_width(self) -> int:
        """Width of the sprite in pixels"""
        return self.bitmap.shape[1]
    
    @property
    def pixel_height(self) -> int:
        """Height of the sprite in pixels"""
        return self.bitmap.shape[0]
    
    @property
    def physical_width(self) -> float:
        """Width of the sprite in millimeters"""
        return px_to_mm(self.pixel_width, dpi=self.dpi)
    
    @property
    def physical_height(self) -> float:
        """Height of the sprite in millimiters"""
        return px_to_mm(self.pixel_height, dpi=self.dpi)
    
    @property
    def pixels_bbox(self) -> Rectangle:
        """Sprite bounding box in its pixel space, that is:
        (0, 0, px_width, px_height)"""
        return Rectangle(0, 0, self.pixel_width, self.pixel_height)
    
    @classmethod
    def many_of_space(cls, space: AffineSpace):
        return cls.many_of(space, lambda s: s.space)
    
    def get_pixels_to_origin_space_transform(self) -> Transform:
        """Returns a transform that converts from local pixel space
        to sprite's origin space (excluding the sprite transform property)"""
        return (
            Transform.translate(Vector2(
                -self.bitmap_origin.x * self.pixel_width,
                -self.bitmap_origin.y * self.pixel_height
            ))
            .then(Transform.scale(px_to_mm(1, dpi=self.dpi)))
        )
    
    def get_pixels_to_parent_space_transform(self) -> Transform:
        """Returns a transform that converts from local pixel space
        to sprite's parent affine space coordinate"""
        return self.get_pixels_to_origin_space_transform().then(self.transform)
    
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
        pixel_width = max(int(mm_to_px(rectangle.width, dpi=dpi)), 1)
        pixel_height = max(int(mm_to_px(rectangle.height, dpi=dpi)), 1)
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

    @staticmethod
    def traverse_sprites(
        root_space: AffineSpace,
        include_pixels_transform=True,
        include_sprite_transform=True,
        include_root_space_transform=False
    ) -> List[Tuple["Sprite", Transform]]:
        """Returns sprites with composed transforms in a givem space.

        The visiting algorithm starts in the given space (considered the root
        space) and then iterates sprites in the rendering order and returns
        them together with their corresponding transforms that map from the
        pixel space back to the root space.

        :param root_space: The root affine space, where the traversal starts and
            where the returnd transforms map to.
        :param include_pixels_transform: Set to false if the transforms should
            map from the sprite's origin space, not from the pixel space.
        :param include_sprite_transform: Set to false if the transforms should
            map from the sprite's parent affine space, not from the sprite's
            origin space. When this flag is false, the pixels transform must
            also be false.
        :param include_root_space_transform: Set to true if you also want to
            includethe transform from the the root space, to the root's parent
            space.
        """
        visitor = SpriteVisitor(
            space=root_space,
            transform_to_root_space=(
                root_space.transform if include_root_space_transform
                else Transform.identity()
            ),
            include_pixels_transform=include_pixels_transform,
            include_sprite_transform=include_sprite_transform,
        )
        visitor.run()
        return visitor.pairs


class SpriteVisitor(AffineSpaceVisitor):
    """Returns a flat list of sprites and transforms to root space.
    
    Use the `Sprite.traverse_sprites()` function instead of this class.
    """

    def __init__(
        self,
        space: AffineSpace,
        transform_to_root_space: Transform,
        include_pixels_transform=True,
        include_sprite_transform=True,
    ):
        super().__init__(space)

        if include_pixels_transform and not include_sprite_transform:
            raise ValueError(
                "You cannot include pixels transform, but not the sprite " +
                "transform. The resulting transform would be nonsensical."
            )
        
        self.transform_to_root_space = transform_to_root_space
        self.include_pixels_transform = include_pixels_transform
        self.include_sprite_transform = include_sprite_transform

        self.pairs: List[Tuple[Sprite, Transform]] = []

    def create_sub_visitor(self, sub_space: AffineSpace) -> "SpriteVisitor":
        return SpriteVisitor(
            space=sub_space,
            transform_to_root_space=sub_space.transform.then(
                self.transform_to_root_space
            ),
            include_pixels_transform=self.include_pixels_transform,
            include_sprite_transform=self.include_sprite_transform,
        )

    def accept_sub_visitor(self, sub_visitor: "SpriteVisitor"):
        self.pairs += sub_visitor.pairs

    def visit_scene_object(self, obj: SceneObject):
        if isinstance(obj, Sprite):
            sprite = obj

            transform = Transform.identity()
            if self.include_pixels_transform:
                transform = transform.then(
                    sprite.get_pixels_to_origin_space_transform()
                )
            if self.include_sprite_transform:
                transform = transform.then(sprite.transform)
            
            full_transform = transform.then(self.transform_to_root_space)

            self.pairs.append((obj, full_transform))
