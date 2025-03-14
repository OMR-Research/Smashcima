import random
import time
from tkinter import Image
from turtle import back
from typing import Tuple

import albumentations as A
import augraphy
import cv2
import numpy as np
from augraphy import (AugraphyPipeline, BleedThrough, DirtyDrum, DirtyRollers,
                      InkBleed, default_augraphy_pipeline)

from smashcima.geometry.units import mm_to_px

from .Canvas import Canvas
from .Filter import Filter
from .FilterStack import FilterStack
from .ImageLayer import ImageLayer
from .LayerSet import LayerSet
from .Postprocessor import Postprocessor


class BaseHandwrittenPostprocessor(Postprocessor):
    """Applies no postprocessing filters."""
    def __init__(self, rng: random.Random):
        
        self.f_stafflines = FilterStack([
            _DilateStafflines(rng),
            _Letterpress(rng),
            _InkColor(rng, reduce_opacity_by=(0.4, 0.9))
        ], rng)

        self.f_inkstyle = FilterStack([
            # caligraphy
            # median vs. inkbleed vs. letterpress
            _Letterpress(rng)
        ], rng)

        self.f_ink_color = _InkColor(rng, reduce_opacity_by=(0.0, 0.3))

        self.f_folding = _Folding(rng)

        self.f_camera = FilterStack([
            _Geometric(rng),
            _ShadowCast(rng),
            _LightingGradient(rng)
            # blur vs. subtle noise
        ], rng)
    
    def process_extracted_layers(
        self,
        layers: LayerSet
    ) -> LayerSet:
        ink = layers["ink"]
        stafflines = layers["stafflines"]
        paper = layers["paper"]
        
        # process stafflines
        stafflines = self.f_stafflines(stafflines)

        # process ink
        ink = self.f_inkstyle(ink)
        # TODO: bleed through
        ink = self.f_ink_color(ink)

        # transform = A.Compose([
        #     A.ThinPlateSpline(p=1)
        #     # A.Blur(blur_limit=31, p=1)
        #     # A.GridElasticDeform(
        #     #     num_grid_xy=(10, 10),
        #     #     magnitude=int(mm_to_px(20, dpi=dpi)),
        #     #     p=1
        #     # )
        # ], seed=42)
        
        # # do the transform
        # layers["ink"].bitmap = transform(
        #     image=layers["ink"].bitmap
        # )["image"]

        # transform = A.Compose([
        #     A.ThinPlateSpline(p=1)
        #     # A.Blur(blur_limit=31, p=1)
        #     # A.GridElasticDeform(
        #     #     num_grid_xy=(10, 10),
        #     #     magnitude=int(mm_to_px(20, dpi=dpi)),
        #     #     p=1
        #     # )
        # ], seed=42)
        
        # layers["stafflines"].bitmap = transform(
        #     image=layers["stafflines"].bitmap
        # )["image"]

        ################################

        # pipeline = AugraphyPipeline(
        #     ink_phase=[
        #         BleedThrough(
        #             intensity_range=(0.1, 0.3),
        #             color_range=(32, 224),
        #             ksize=(17, 17),
        #             sigmaX=1,
        #             alpha=random.uniform(0.1, 0.2),
        #             offsets=(10, 20),
        #         ),
        #     ],
        #     paper_phase=[],
        #     post_phase=[]
        # )

        # augmentation = DirtyRollers()

        # layers["paper"].bitmap = augmentation(
        #     image=layers["paper"].bitmap
        # )

        return LayerSet({
            "ink": ink,
            "stafflines": stafflines,
            "paper": paper
        })
    
    def process_final_layer(
        self,
        final_layer: ImageLayer
    ) -> ImageLayer:
        
        # TODO: scribbles and stains
        final_layer = self.f_folding(final_layer)
        final_layer = self.f_camera(final_layer)
        
        # transform = A.Compose([
        #     A.ThinPlateSpline(p=1)
        # ], seed=42)

        # final_layer.bitmap = transform(
        #     image=final_layer.bitmap
        # )["image"]

        #################x

        # pipeline = default_augraphy_pipeline()

        # pipeline = AugraphyPipeline(
        #     ink_phase=[],
        #     paper_phase=[],
        #     post_phase=[]
        # )

        # final_layer.bitmap = pipeline(
        #     image=final_layer.bitmap
        # )

        return final_layer


class _ShadowCast(Filter):
    """Applies the Augraphy ShadowCast filter to the composed image"""
    def apply_to(self, input: ImageLayer) -> ImageLayer:
        # make augraphy deterministic and call it
        random.seed(self.rng.random())
        augmentation = augraphy.ShadowCast()
        bitmap = augmentation(input.bitmap)
        
        return ImageLayer(
            bitmap=bitmap,
            dpi=input.dpi,
            space=input.space,
            regions=input.regions
        )


class _LightingGradient(Filter):
    """Applies the Augraphy LightingGradient filter to the composed image"""
    def apply_to(self, input: ImageLayer) -> ImageLayer:
        # make augraphy deterministic and call it
        random.seed(self.rng.random())
        augmentation = augraphy.LightingGradient()
        bitmap = augmentation(input.bitmap)
        
        return ImageLayer(
            bitmap=bitmap,
            dpi=input.dpi,
            space=input.space,
            regions=input.regions
        )

class _Geometric(Filter):
    """Applies the Augraphy Geometric filter to the composed image"""
    def apply_to(self, input: ImageLayer) -> ImageLayer:
        # TODO: apply to regions as well
        
        # make augraphy deterministic and call it
        random.seed(self.rng.random())
        augmentation = augraphy.Geometric(
            rotate_range=(-5, 5), # angle in degrees
            padding_value=(0, 0, 0)
        )
        bitmap = augmentation(input.bitmap)
        
        return ImageLayer(
            bitmap=bitmap,
            dpi=input.dpi,
            space=input.space,
            regions=input.regions
        )


class _Folding(Filter):
    """Applies the Augraphy Folding filter to the composed image"""
    def apply_to(self, input: ImageLayer) -> ImageLayer:
        # TODO: apply to regions as well
        
        # make augraphy deterministic and call it
        random.seed(self.rng.random())
        augmentation = augraphy.Folding(
            fold_count=10,
            fold_noise=0.0,
            fold_angle_range=(-360,360),
            gradient_width=(0.1, 0.2),
            gradient_height=(0.005, 0.01),
            backdrop_color=(0,0,0),
        )
        pad = augraphy.Geometric(
            padding=[0.01]*4,
            padding_value=(0, 0, 0)
        )
        bitmap = augmentation(pad(input.bitmap))
        
        return ImageLayer(
            bitmap=bitmap,
            dpi=input.dpi,
            space=input.space,
            regions=input.regions
        )


class _InkColor(Filter):
    """Colors the ink to a single color and adjusts transparency"""
    def __init__(self,
        rng: random.Random,
        reduce_opacity_by: Tuple[float, float],
        max_saturation_pct: float = 0.8,
        max_lightness_pct: float = 0.2,
        p: float = 1.0
    ):
        super().__init__(rng, p)
        self.reduce_opacity_by = reduce_opacity_by
        self.max_saturation_pct = max_saturation_pct
        self.max_lightness_pct = max_lightness_pct
    
    def sample_ink_bgr_uint8_color(self) -> Tuple[int, int, int]:
        hue = self.rng.randint(0, 180) # openCV uint8 hue range is 0-180
        lightness = self.rng.uniform(0.0, self.max_lightness_pct) * 255
        saturation = self.rng.uniform(0.0, self.max_saturation_pct) * 255

        b, g, r = cv2.cvtColor(
            np.array([[[hue, lightness, saturation]]], dtype=np.uint8),
            cv2.COLOR_HLS2BGR_FULL
        )[0][0]

        return (b, g, r)


    def apply_to(self, input: ImageLayer) -> ImageLayer:
        # start_time = time.time()

        bgr = input.bitmap[:,:,0:3]
        alpha = input.bitmap[:,:,3]

        # choose ink color
        b, g, r = self.sample_ink_bgr_uint8_color()

        # apply ink color
        bgr[:,:,0] = b
        bgr[:,:,1] = g
        bgr[:,:,2] = r

        # adjust transparency
        alpha_multiply = 1.0 - self.rng.uniform(*self.reduce_opacity_by)
        alpha = np.astype(alpha * alpha_multiply, np.uint8)
        
        bitmap = np.concat([bgr, alpha[:,:,np.newaxis]], axis=2)

        # print("InkColor seconds:", (time.time() - start_time))
        
        return ImageLayer(
            bitmap=bitmap,
            dpi=input.dpi,
            space=input.space,
            regions=input.regions
        )


class _Letterpress(Filter):
    """Applies the Augraphy Letterpress filter to an ink layer"""
    def apply_to(self, input: ImageLayer) -> ImageLayer:
        # start_time = time.time()

        # TODO: make it DPI independend

        # collapse alpha to grayscale image (the augraphy ink format)
        c = Canvas(
            width=input.width,
            height=input.height,
            background_color=(255, 255, 255, 255) # white
        )
        c.place_layer(input.bitmap)
        gray = cv2.cvtColor(c.read(), cv2.COLOR_BGRA2GRAY)

        # make augraphy deterministic and call it
        random.seed(self.rng.random())
        augmentation = augraphy.Letterpress()
        gray = augmentation(gray)
        
        # re-intorduce the alpha
        bitmap = np.zeros_like(input.bitmap)
        bitmap[:,:,3] = 255 - gray

        # print("Letterpress seconds:", (time.time() - start_time))

        return ImageLayer(
            bitmap=bitmap,
            dpi=input.dpi,
            space=input.space,
            regions=input.regions
        )


class _DilateStafflines(Filter):
    """Thickens the default naive stafflines. This can be removed or has to
    be modified once a proper stafflines synthesizer is introduced."""
    def apply_to(self, input: ImageLayer) -> ImageLayer:
        # start_time = time.time()

        bgr = input.bitmap[:,:,0:3]
        alpha = input.bitmap[:,:,3]

        dilate_mm = self.rng.uniform(0.2, 0.8)
        dilate_pixels = int(mm_to_px(dilate_mm, dpi=input.dpi))

        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            ksize=(dilate_pixels, dilate_pixels),
        )

        # helps prevent gray stafflines (due to staffline aliasing)
        _, alpha = cv2.threshold(alpha, 32, 255, cv2.THRESH_BINARY)

        alpha = cv2.dilate(alpha, kernel)
        bgr = 255 - cv2.dilate(255 - bgr, kernel)

        bitmap = np.concat([bgr, alpha[:,:,np.newaxis]], axis=2)

        # print("Dilation seconds:", (time.time() - start_time))

        return ImageLayer(
            bitmap=bitmap,
            dpi=input.dpi,
            space=input.space,
            regions=input.regions
        )
