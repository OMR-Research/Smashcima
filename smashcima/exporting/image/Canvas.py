from math import ceil
from typing import Union

import numpy as np
import cv2

from smashcima.geometry.Rectangle import Rectangle


def _premultiplied_float32_alpha_overlay(
    surface: np.ndarray,
    layer: np.ndarray
):
    """Implements the 'alpha overlay' blending method for the surface and
    a top layer that is being blended over. Both must have the same shape.
    The surface array will be modified in-place. Both are expected to be
    in the float32 alpha premultiplied color format."""
    factor = (1 - layer[:, :, 3:4])
    surface *= factor
    surface += layer


def _premultiplied_float32_alpha_overlay_in_window(
    surface: np.ndarray,
    window: Rectangle,
    layer: np.ndarray
):
    """Implements the 'alpha overlay' blending method for the surface and
    a top layer that is being blended over. The top layer is smaller and
    constrained to a window within the underlying surface. The surface array
    will be modified in-place. Both are expected to be in the float32 alpha
    premultiplied color format."""
    assert int(window.height) == layer.shape[0]
    assert int(window.width) == layer.shape[1]
    top = int(window.top)
    bottom = int(window.bottom)
    left = int(window.left)
    right = int(window.right)
    _premultiplied_float32_alpha_overlay(
        surface[top:bottom, left:right],
        layer
    )


def _uint8_to_float32(img: np.ndarray) -> np.ndarray:
    """Converts image from uint8 (0-255) format to float32 (0.0-1.0) format"""
    img = img.astype(np.float32)
    img /= 255
    return img


def _float32_to_uint8(img: np.ndarray) -> np.ndarray:
    """Converts image from float32 (0.0-1.0) format to uint8 (0-255) format"""
    img *= 255
    img = img.astype(np.uint8)
    return img


class Canvas:
    """A tool for composing transparent uint8 BGRA imges over each other"""
    def __init__(
        self,
        width: Union[int, float],
        height: Union[int, float],
        background_color = (0, 0, 0, 0)
    ):
        self.bbox = Rectangle(
            x=0,
            y=0,
            width=ceil(max(width, 1.0)), # at least 1 pixel
            height=ceil(max(height, 1.0)), # at least 1 pixel
        )
        """Bounding box of the canvas in the pixel coordinate space"""

        self.surface = np.zeros(
            shape=(self.height, self.width, 4),
            dtype=np.float32
        )
        """The pixel buffer that we paint over in alpha premultiplied float32
        format (BGRA channels)"""

        # fill the surface with background color
        background_color_premultiplied = _uint8_to_float32(cv2.cvtColor(
            np.array([[background_color]], dtype=np.uint8),
            cv2.COLOR_RGBA2mRGBA
        ))
        self.surface[:, :] = background_color_premultiplied
    
    @property
    def width(self) -> int:
        return int(self.bbox.width)
    
    @property
    def height(self) -> int:
        return int(self.bbox.height)
    
    def place_bitmap(self, bitmap: np.ndarray, window: Rectangle):
        """Overlays a bitmap over the canvas and merges it
        
        :param bitmap: An uint8 BGRA bitmap of the same size as the window.
        :param window: The positioning of the bitmap over the canvas.
            It must be fully inside the canvas bbox.
        """
        intersected_window = window.intersect_with(self.bbox)
        assert intersected_window.width == window.width \
            and intersected_window.height == window.height, \
            "Window must be fully inside the canvas bbox"
        
        # prepare the bitmap into mBGRA float
        bitmap = cv2.cvtColor(bitmap, cv2.COLOR_RGBA2mRGBA)
        bitmap = _uint8_to_float32(bitmap)
        
        # composit the layer over the surface in the window
        _premultiplied_float32_alpha_overlay_in_window(
            self.surface, window, bitmap
        )
    
    def place_layer(self, layer: np.ndarray):
        """Overlays a layer (bitmap of the same size as the canvas)
        and merges it
        
        :param layer: An uint8 BGRA bitmap of the same size as the canvas.
        """
        assert layer.shape[0] == self.height
        assert layer.shape[1] == self.width
        self.place_bitmap(layer, Rectangle(0, 0, self.width, self.height))
    
    def read(self) -> np.ndarray:
        """Returns the current canvas state as uint8 BGRA bitmap"""
        return cv2.cvtColor(
            _float32_to_uint8(self.surface),
            cv2.COLOR_mRGBA2RGBA
        )
