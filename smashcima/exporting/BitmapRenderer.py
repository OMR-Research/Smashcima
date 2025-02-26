from math import ceil
from typing import Tuple

import cv2
import numpy as np

from smashcima.geometry import Quad, Rectangle, Transform, mm_to_px
from smashcima.scene import Sprite, ViewBox

# Alpha compositing via the "over" operator + alpha premultiplication:
# https://en.wikipedia.org/wiki/Alpha_compositing


def _premultiplied_float32_alpha_overlay(canvas: np.ndarray, layer: np.ndarray):
    factor = (1 - layer[:, :, 3:4])
    canvas *= factor
    canvas += layer


def _premultiplied_float32_alpha_overlay_in_window(
    canvas: np.ndarray,
    window: Rectangle,
    layer: np.ndarray
):
    assert int(window.height) == layer.shape[0]
    assert int(window.width) == layer.shape[1]
    top = int(window.top)
    bottom = int(window.bottom)
    left = int(window.left)
    right = int(window.right)
    _premultiplied_float32_alpha_overlay(
        canvas[top:bottom, left:right],
        layer
    )


def _uint8_to_float32(img: np.ndarray) -> np.ndarray:
    img = img.astype(np.float32)
    img /= 255
    return img


def _float32_to_uint8(img: np.ndarray) -> np.ndarray:
    img *= 255
    img = img.astype(np.uint8)
    return img


class BitmapRenderer:
    """Renders a scene into a bitmap RGBA opencv representation"""
    def __init__(
        self,
        dpi: float = 300,
        background_color = (0, 0, 0, 0)
    ):
        self.dpi = float(dpi)
        """DPI at which the scene should be rasterized"""

        self.background_color: Tuple[int, int, int, int] = background_color
        """Color to use for the blank canvas, transparent by default
        (BGRA uint8 format)"""

    def render(self, view_box: ViewBox) -> np.ndarray:
        # bounding box of the canvas in pixel space
        canvas_px_bbox = Rectangle(
            x=0,
            y=0,
            width=ceil(mm_to_px(view_box.rectangle.width, dpi=self.dpi)),
            height=ceil(mm_to_px(view_box.rectangle.height, dpi=self.dpi)),
        )

        # canvas cannot be zero-sized
        if canvas_px_bbox.width == 0:
            canvas_px_bbox.width = 1
        if canvas_px_bbox.height == 0:
            canvas_px_bbox.height = 1

        # the canvas pixel array in alpha premultiplied float32 format
        canvas = np.zeros(
            shape=(int(canvas_px_bbox.height), int(canvas_px_bbox.width), 4),
            dtype=np.float32
        )

        # fill with background color
        background_color_premultiplied = _uint8_to_float32(cv2.cvtColor(
            np.array([[self.background_color]], dtype=np.uint8),
            cv2.COLOR_RGBA2mRGBA
        ))
        canvas[:, :] = background_color_premultiplied

        # converts from scene millimeter coordinate system
        # to the canvas pixel coordinate system
        scene_to_canvas_transform = (
            Transform.translate(-view_box.rectangle.top_left_corner.vector)
                .then(Transform.scale(mm_to_px(1, dpi=self.dpi)))
        )

        # root scene space
        root_space = view_box.space.get_root()

        # go through all the sprites in the scene
        for (sprite, sprite_transform) in Sprite.traverse_sprites(
            root_space,
            include_pixels_transform=True,
            include_sprite_transform=True,
            include_root_space_transform=False
        ):
            # build up a transform that converts from sprite's local pixel space
            # to canvas global pixel space, while going through the scene space
            to_canvas_transform = (
                sprite_transform # recursive scene hierarchy transforms
                .then(scene_to_canvas_transform)
            )

            # get the window in the canvas that we're going to paint over
            canvas_window: Rectangle = (
                to_canvas_transform.apply_to(
                    Quad.from_rectangle(
                        sprite.pixels_bbox.dilate(1.0) # grow by 1 pixel
                        # dilation is done to accommodate the aliasing blur
                    )
                ) # get the quad of the dilated sprite quad in canvas coordinates
                .bbox() # get the bounding box rectangle
                .snap_grow() # round to integer by growing
                .intersect_with(canvas_px_bbox) # clamp inside of canvas
            )
            to_window_transform = to_canvas_transform.then(
                Transform.translate(-canvas_window.top_left_corner.vector)
            )

            # viewport culling:
            # do not render sprites that have no overlap with the canvas
            if canvas_window.has_no_area:
                continue

            # prepare the sprite bitmap into mRGBA float
            sprite_bitmap = sprite.bitmap
            sprite_bitmap = cv2.cvtColor(sprite_bitmap, cv2.COLOR_RGBA2mRGBA)
            sprite_bitmap = _uint8_to_float32(sprite_bitmap)

            # get the transformed bitmap of the sprite
            new_layer = cv2.warpAffine(
                src=sprite_bitmap,
                M=to_window_transform.matrix,
                dsize=(int(canvas_window.width), int(canvas_window.height)),
                flags=(
                    cv2.INTER_AREA # used for downscaling
                    if to_window_transform.determinant < 1.0
                    else cv2.INTER_LINEAR # used for upscaling
                ),
                borderMode=cv2.BORDER_CONSTANT
            )

            # composit the next layer over the canvas in the window
            _premultiplied_float32_alpha_overlay_in_window(
                canvas, canvas_window, new_layer
            )

        # convert to uint8 RGBA (BGRA actually) and return
        return cv2.cvtColor(
            _float32_to_uint8(canvas),
            cv2.COLOR_mRGBA2RGBA
        )
