from typing import List

import cv2

from smashcima.geometry.Quad import Quad
from smashcima.geometry.Rectangle import Rectangle
from smashcima.geometry.Transform import Transform
from smashcima.scene.AffineSpace import AffineSpace
from smashcima.scene.LabeledRegion import LabeledRegion
from smashcima.scene.Sprite import Sprite

from .Canvas import Canvas
from .ImageLayer import ImageLayer


class ImageLayerBuilder:
    """Gradually builds an ImageLayer by accepting sprites and regions"""
    
    def __init__(self, width: int, height: int, dpi: float):
        self.canvas = Canvas(width, height)
        """Builds up the bitmap"""

        self.dpi = dpi
        """DPI of the build up image layer"""

        self.space = AffineSpace()
        """The spce to which all the built up regions belong"""

        self.regions: List[LabeledRegion] = []
        """Builds up regions"""

    def build_layer(self) -> ImageLayer:
        """Builds up a layer instance from the so-far received objects"""
        return ImageLayer(
            bitmap=self.canvas.read(),
            dpi=self.dpi,
            space=self.space,
            regions=self.regions
        )
    
    def add_sprite(self, sprite: Sprite, space_to_canvas_transform: Transform):
        """Adds a sprite bitmap into the layer
        
        :param sprite: The sprite to add.
        :param space_to_canvas_transform: Transforms from the sprite's parent
            affine space to the pixel space of the layer bitmap (the canvas).
        """
        pixels_to_canvas_transform = (
            sprite.get_pixels_to_parent_space_transform()
            .then(space_to_canvas_transform)
        )

        # get the window in the canvas that we're going to paint over
        canvas_window: Rectangle = (
            pixels_to_canvas_transform.apply_to(
                Quad.from_rectangle(
                    sprite.pixels_bbox.dilate(1.0) # grow by 1 pixel
                    # dilation is done to accommodate the aliasing blur
                )
            ) # get the quad of the dilated sprite quad in canvas coordinates
            .bbox() # get the bounding box rectangle
            .snap_grow() # round to integer by growing
            .intersect_with(self.canvas.bbox) # clamp inside of canvas
        )
        pixels_to_window_transform = pixels_to_canvas_transform.then(
            Transform.translate(-canvas_window.top_left_corner.vector)
        )

        # viewport culling:
        # do not render sprites that have no overlap with the canvas
        if canvas_window.has_no_area:
            return
        
        # transform the sprite bitmap into the canvas pixel space
        new_layer = cv2.warpAffine(
            src=sprite.bitmap,
            M=pixels_to_window_transform.matrix,
            dsize=(int(canvas_window.width), int(canvas_window.height)),
            flags=(
                cv2.INTER_AREA # used for downscaling
                if pixels_to_window_transform.determinant < 1.0
                else cv2.INTER_LINEAR # used for upscaling
            ),
            borderMode=cv2.BORDER_CONSTANT
        )
        
        # place the transformed bitmap into the canvas
        self.canvas.place_bitmap(
            bitmap=new_layer,
            window=canvas_window
        )
    
    def add_region(
        self,
        region: LabeledRegion,
        space_to_canvas_transform: Transform
    ):
        """Adds a labeled region into the layer
        
        :param region: The labeled region to add.
        :param space_to_canvas_transform: Transforms from the region's parent
            affine space to the pixel space of the layer bitmap (the canvas).
        """
        transformed_contours = space_to_canvas_transform.apply_to(
            region.contours
        )
        
        canvas_window: Rectangle = (
            transformed_contours
                .bbox()
                .intersect_with(self.canvas.bbox)
        )

        # viewport culling:
        # do not include regions that have no overlap with the canvas
        if canvas_window.has_no_area:
            return

        self.regions.append(LabeledRegion(
            space=self.space,
            contours=transformed_contours,
            label=region.label
        ))
    
    @staticmethod
    def merge_layers(layers: List["ImageLayer"]) -> "ImageLayer":
        """Merges layers into a single layer"""
        assert len(layers) > 0, "There must be at least one layer"
        width = layers[0].width
        height = layers[0].height
        dpi = layers[0].dpi

        builder = ImageLayerBuilder(
            width=width,
            height=height,
            dpi=dpi
        )
        identity = Transform.identity()
        
        for layer in layers:
            assert builder.dpi == layer.dpi, "All layers must have the same DPI"
            builder.canvas.place_layer(layer.bitmap)
            
            for region in layer.regions:
                builder.add_region(
                    region=region,
                    space_to_canvas_transform=identity
                )
        
        return builder.build_layer()
