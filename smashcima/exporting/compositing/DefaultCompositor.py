from math import ceil
from typing import Optional

from smashcima.geometry.Transform import Transform
from smashcima.geometry.units import mm_to_px
from smashcima.scene.AffineSpace import AffineSpace
from smashcima.scene.AffineSpaceVisitor import AffineSpaceVisitor
from smashcima.scene.ComposedGlyph import ComposedGlyph
from smashcima.scene.Glyph import Glyph
from smashcima.scene.LabeledRegion import LabeledRegion
from smashcima.scene.SceneObject import SceneObject
from smashcima.scene.SmashcimaLabels import SmashcimaLabels
from smashcima.scene.Sprite import Sprite
from smashcima.scene.ViewBox import ViewBox
from smashcima.scene.visual.StaffVisual import StaffVisual

from .Compositor import Compositor
from ..image.ImageLayer import ImageLayer
from ..image.ImageLayerBuilder import ImageLayerBuilder
from ..image.LayerSet import LayerSet
from ..postprocessing.Postprocessor import Postprocessor


class DefaultCompositor(Compositor):
    """Composits the scene into a single image by first extracting three
    layers: paper, stafflines, and ink. Then it applies the postprocessor
    to them. Then they are merged via the alpha channel and finally the
    postprocessor is called again on the composed image.
    
    This compositing setup is the default setup for Smashcima. If you want
    something different, you need to implement your own compositor."""

    def __init__(self, postprocessor: Postprocessor):
        self.postprocessor = postprocessor

    def run(self, view_box: ViewBox, dpi: float) -> ImageLayer:
        extracted_layers = self.extract_layers(view_box, dpi)
        
        processed_layers = self.postprocessor.process_extracted_layers(
            extracted_layers
        )
        
        final_layer = ImageLayerBuilder.merge_layers([
            processed_layers["paper"],
            processed_layers["stafflines"],
            processed_layers["ink"]
        ])
    
        processed_final_layer = self.postprocessor.process_final_layer(
            final_layer
        )

        return processed_final_layer
    
    def extract_layers(self, view_box: ViewBox, dpi: float) -> LayerSet:
        accumulator = VisitorAccumulator(
            width=ceil(mm_to_px(view_box.rectangle.width, dpi=dpi)),
            height=ceil(mm_to_px(view_box.rectangle.height, dpi=dpi)),
            dpi=dpi
        )

        # TODO: this code assumes the view box is in the root affine space
        # modify it to relax this assumption (so that we can have,
        # say view boxes on indivudal glyphs)

        # converts from scene millimeter coordinate system
        # to the canvas pixel coordinate system
        scene_to_canvas_transform = (
            Transform.translate(-view_box.rectangle.top_left_corner.vector)
                .then(Transform.scale(mm_to_px(1, dpi=dpi)))
        )

        # root scene space
        root_space = view_box.space.get_root()
        
        # visit objects in the scene and build up layers
        visitor = SceneVisitor(
            space=root_space,
            accumulator=accumulator,
            space_to_canvas_transform=scene_to_canvas_transform
        )
        visitor.run()

        return accumulator.build_layer_set()


class VisitorAccumulator:
    """Accumulates data extracted by the visitor"""
    def __init__(self, width: int, height: int, dpi: float):
        # the three extracted layers
        self.paper = ImageLayerBuilder(width=width, height=height, dpi=dpi)
        self.stafflines = ImageLayerBuilder(width=width, height=height, dpi=dpi)
        self.ink = ImageLayerBuilder(width=width, height=height, dpi=dpi)
    
    def build_layer_set(self) -> LayerSet:
        return LayerSet({
            "paper": self.paper.build_layer(),
            "stafflines": self.stafflines.build_layer(),
            "ink": self.ink.build_layer()
        })


class SceneVisitor(AffineSpaceVisitor):
    """Visits an AffineSpace hierarchy and distributes objects into layers"""
    
    def __init__(
        self,
        space: AffineSpace,
        accumulator: VisitorAccumulator,
        space_to_canvas_transform: Transform
    ):
        super().__init__(space)
        self.accumulator = accumulator
        self.space_to_canvas_transform = space_to_canvas_transform
    
    def create_sub_visitor(self, sub_space: AffineSpace) -> "SceneVisitor":
        return SceneVisitor(
            sub_space,
            self.accumulator,
            sub_space.transform.then(self.space_to_canvas_transform)
        )

    def accept_sub_visitor(self, sub_visitor: "SceneVisitor"):
        # nothing - all visitors write to the same accumulator instance
        pass

    def visit_scene_object(self, obj: SceneObject):
        if isinstance(obj, Sprite):
            self.get_layer_for_sprite(obj).add_sprite(
                sprite=obj,
                space_to_canvas_transform=self.space_to_canvas_transform
            )
        elif isinstance(obj, LabeledRegion):
            self.get_layer_for_region(obj).add_region(
                region=obj,
                space_to_canvas_transform=self.space_to_canvas_transform
            )
    
    def get_layer_for_sprite(self, sprite: Sprite) -> ImageLayerBuilder:
        # get the glyph of the sprite
        glyphs = Glyph.many_of(sprite, lambda g: g.sprites)
        glyphs = [g for g in glyphs if not isinstance(g, ComposedGlyph)]
        glyph = None
        if len(glyphs) > 0:
            glyph = glyphs[0]

        return self.get_layer_for_glyph(glyph)

    def get_layer_for_region(self, region: LabeledRegion) -> ImageLayerBuilder:
        # get the glyph of the region
        glyphs = Glyph.many_of(region, lambda g: g.region)
        glyphs = [g for g in glyphs if not isinstance(g, ComposedGlyph)]
        glyph = None
        if len(glyphs) > 0:
            glyph = glyphs[0]

        return self.get_layer_for_glyph(glyph)
    
    def get_layer_for_glyph(self, glyph: Optional[Glyph]) -> ImageLayerBuilder:
        # object outside of a glyph is the paper background
        if glyph is None:
            return self.accumulator.paper
        
        # staffline glyphs belong to the stafflines layer
        if glyph.region.label == SmashcimaLabels.staffLine.value:
            return self.accumulator.stafflines
        
        # what remains is the ink layer
        return self.accumulator.ink
