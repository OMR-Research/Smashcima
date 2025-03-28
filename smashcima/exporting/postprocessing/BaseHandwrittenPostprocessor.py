import random
import sys
import time
from typing import Tuple

import augraphy
import cv2
import numpy as np

from smashcima.geometry.units import mm_to_px

from ..image.Canvas import Canvas
from ..image.ImageLayer import ImageLayer
from ..image.LayerSet import LayerSet
from .Filter import Filter
from .FilterStack import FilterStack
from .Postprocessor import Postprocessor


class BaseHandwrittenPostprocessor(Postprocessor):
    """Applies no postprocessing filters."""
    def __init__(self, rng: random.Random):
        
        self.f_stafflines = FilterStack([
            _DilateStafflines(rng),
            _Letterpress(rng, p=0.5),
            _InkColor(rng, reduce_opacity_by=(0.4, 0.9))
        ], rng)

        self.f_inkstyle = FilterStack([
            # add caligraphy here (p=0.3)
            _Median(rng, p=0.3),
            _InkBleed(rng, p=0.3),
            _Letterpress(rng, p=0.5)
        ], rng)

        self.f_bleed_through = _BleedThrough(rng, p=0.5)

        self.f_ink_color = _InkColor(rng, reduce_opacity_by=(0.0, 0.3))

        self.f_scribbles = _Scribbles(rng, p=0.5)

        self.f_folding = _Folding(rng, p=0.5)

        self.f_camera = FilterStack([
            _Geometric(rng, p=0.5),
            _ShadowCast(rng, p=0.5),
            _LightingGradient(rng, p=0.5),
            _Blur(rng, p=0.5)
            # add subtle noise here
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
        ink = self.f_bleed_through(ink)
        ink = self.f_ink_color(ink)

        return LayerSet({
            "ink": ink,
            "stafflines": stafflines,
            "paper": paper
        })
    
    def process_final_layer(
        self,
        final_layer: ImageLayer
    ) -> ImageLayer:
        final_layer = self.f_scribbles(final_layer)
        final_layer = self.f_folding(final_layer)
        final_layer = self.f_camera(final_layer)
        return final_layer


class _Blur(Filter):
    """Applies the Albumentations Blur filter to the composed image"""
    def apply_to(self, input: ImageLayer) -> ImageLayer:
        # lazy import albumentations (it makes an HTTP version check call)
        import albumentations as A

        ksize = max(int(mm_to_px(self.rng.uniform(0.5, 3.0), dpi=input.dpi)), 1)

        transform = A.Compose([
            A.Blur(
                blur_limit=ksize,
                p=1
            )
        ], seed=self.rng.randint(0, sys.maxsize))

        bitmap = transform(image=input.bitmap)["image"]
        
        return ImageLayer(
            bitmap=bitmap,
            dpi=input.dpi,
            space=input.space,
            regions=input.regions
        )


class _Median(Filter):
    """Applies a median filter to a layer to simulate liquid ink shape smoothing"""
    def apply_to(self, input: ImageLayer) -> ImageLayer:
        ksize = max(int(mm_to_px(self.rng.uniform(0.05, 0.4), dpi=input.dpi)), 1)

        bitmap = cv2.medianBlur(
            input.bitmap,
            ksize=ksize*2+1
        )
        
        return ImageLayer(
            bitmap=bitmap,
            dpi=input.dpi,
            space=input.space,
            regions=input.regions
        )


class _InkBleed(Filter):
    """Applies the Augraphy InkBleed filter to the composed image"""
    def apply_to(self, input: ImageLayer) -> ImageLayer:
        # collapse alpha to grayscale image (the augraphy ink format)
        gray = smashcima_bgra_to_augraphy_gray(input.bitmap)

        ksize = max(int(mm_to_px(self.rng.uniform(0.05, 0.3), dpi=input.dpi)), 1)

        # make augraphy deterministic and call it
        random.seed(self.rng.random())
        augmentation = augraphy.InkBleed(
            intensity_range=(0.4, 0.7),
            kernel_size=(ksize*2+1, ksize*2+1),
            severity=(0.2, 0.4)
        )
        gray = augmentation(gray)

        # re-intorduce the alpha
        bitmap = augraphy_gray_to_smashcima_bgra(gray)
        # bitmap = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGRA)
        
        return ImageLayer(
            bitmap=bitmap,
            dpi=input.dpi,
            space=input.space,
            regions=input.regions
        )


class _Scribbles(Filter):
    """Applies the Augraphy Scribbles filter to the composed image"""
    def apply_to(self, input: ImageLayer) -> ImageLayer:
        size_from_px = int(mm_to_px(10.0, dpi=input.dpi)) # 1 cm
        size_to_px = int(mm_to_px(50.0, dpi=input.dpi)) # 5 cm
        
        # make augraphy deterministic and call it
        random.seed(self.rng.random())
        augmentation = augraphy.Scribbles(
            scribbles_type="random",
            scribbles_ink="random",
            scribbles_location="random",
            scribbles_size_range=(size_from_px, size_to_px),
            scribbles_count_range=(1, 6),
            scribbles_thickness_range=(1, 3),
            scribbles_brightness_change=[8, 16],
            scribbles_skeletonize=0,
            scribbles_skeletonize_iterations=(2, 3),
            scribbles_color="random",
            scribbles_text="random",
            scribbles_text_font="random",
            scribbles_text_rotate_range=(0, 360),
            scribbles_lines_stroke_count_range=(1, 6),
        )
        bitmap = augmentation(input.bitmap)
        
        return ImageLayer(
            bitmap=bitmap,
            dpi=input.dpi,
            space=input.space,
            regions=input.regions
        )


class _BleedThrough(Filter):
    """Applies the Augraphy BleedThrough filter to the composed image"""
    def apply_to(self, input: ImageLayer) -> ImageLayer:
        # collapse alpha to grayscale image (the augraphy ink format)
        gray = smashcima_bgra_to_augraphy_gray(input.bitmap)

        ksize = max(int(mm_to_px(self.rng.uniform(0.1, 0.7), dpi=input.dpi)), 1)
        offsets=(
            int(mm_to_px(self.rng.uniform(-10, 10), dpi=input.dpi)),
            int(mm_to_px(self.rng.uniform(-5, 5), dpi=input.dpi))
        )

        # make augraphy deterministic and call it
        random.seed(self.rng.random())
        augmentation = augraphy.BleedThrough(
            intensity_range=(0.1, 0.3),
            color_range=(32, 224),
            ksize=(ksize*2+1, ksize*2+1),
            sigmaX=1,
            alpha=self.rng.uniform(0.1, 0.5),
            offsets=offsets,
        )
        gray = augmentation(gray)

        # re-intorduce the alpha
        bitmap = augraphy_gray_to_smashcima_bgra(gray)
        # bitmap = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGRA)
        
        return ImageLayer(
            bitmap=bitmap,
            dpi=input.dpi,
            space=input.space,
            regions=input.regions
        )


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
        gray = smashcima_bgra_to_augraphy_gray(input.bitmap)

        # make augraphy deterministic and call it
        random.seed(self.rng.random())
        augmentation = augraphy.Letterpress()
        gray = augmentation(gray)
        
        # re-intorduce the alpha
        bitmap = augraphy_gray_to_smashcima_bgra(gray)

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


def smashcima_bgra_to_augraphy_gray(bitmap: np.ndarray) -> np.ndarray:
    """Converts smashcima BGRA image with black ink on transparent to the
    augraphy ink grayscale, where white means kinda-transparent"""
    c = Canvas(
        width=bitmap.shape[1],
        height=bitmap.shape[0],
        background_color=(255, 255, 255, 255) # white
    )
    c.place_layer(bitmap)
    gray = cv2.cvtColor(c.read(), cv2.COLOR_BGRA2GRAY)
    return gray


def augraphy_gray_to_smashcima_bgra(gray: np.ndarray) -> np.ndarray:
    """Converts augraphy grayscale black on white to smashcima BGRA transparent
    by interpreting the lightness as transparency and setting color everywhere
    to pitch black"""
    assert len(gray.shape) == 2
    bitmap = np.zeros(shape=(*gray.shape, 4), dtype=np.uint8)
    bitmap[:,:,3] = 255 - gray
    return bitmap
