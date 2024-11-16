from dataclasses import dataclass
from typing import List

from smashcima.geometry import Contours

from .AffineSpace import AffineSpace
from .Glyph import Glyph
from .LabeledRegion import LabeledRegion
from .Sprite import Sprite


@dataclass
class ComposedGlyph(Glyph):
    """A group of glyphs that make up a larger logical glyph.

    Sometimes a glyph can be represented as a whole, but can also be rendered
    as a group of smaller glyphs. Always forcing the rendering from parts
    might be detremental, because we might not have the assets to synthesize
    from. But if we allow rendering larger glyphs, they may be:
    1) a ligature which can be rendered as a whole thing or nothing
    2) a composite which can be split up into parts
    If we allow rendering the first part, we loose the subparts, and that's
    a compromise we have to make. However with the second part, we can preserve
    the information about the composition.

    Sub-glyphs should have their parent space linked to this glyph's space.
    
    Sprites in this glyph MUST be the union of sprites of subglyphs,
    so that all the external users can access this property.
    You can do so by calling aggregate_sprites() once the glyph is built.
    
    Methods here have to be overriden to make this collection-glyph behave
    properly.

    This is not really a ligature, as a ligature is something that cannot be
    more subdivided. But when it can be, it will be represented by this class.
    So this class is like a "decomposable" ligature.
    """
    
    sub_glyphs: List[Glyph]
    """Glyphs that make up this larger glyph"""

    def detach(self):
        """Unlink the glyph from the scene"""
        super().detach()
        for g in self.sub_glyphs:
            g.detach()
        self.sub_glyphs = []

    @staticmethod
    def build(label: str, sub_glyphs: List[Glyph]) -> "ComposedGlyph":
        """Builds a composed glyph from a collection of its sub-glyphs.

        Given sub-glyphs must not be attached to the scene yet, meaning their
        space must have no parent space. Their relative position within the
        composed glyph's space must be set by configuring their transform
        before (or after) they are passed into this fuction.

        These glyphs will be attached to the newly constructed composed
        glyph's space, their sprites will be referenced directly and their
        regions will be used to compute the unified region for the composed
        glyph.

        :param label: Classification label for the composed glyph
        :param sub_glyphs: Glyphs that will be included in the composed glyph
        """
        space = AffineSpace()

        assert all(g.space.parent_space is None for g in sub_glyphs), \
            "Given sub-glyphs must NOT be attached to the scene"
        
        # attach sub glyphs under the new root space
        for g in sub_glyphs:
            g.space.parent_space = space
        
        # gather sprites
        sprites: List[Sprite] = [s for g in sub_glyphs for s in g.sprites]

        # gather contours
        contours = Contours([
            c for g in sub_glyphs
            for c in g.region.get_contours_in_space(space).polygons
        ])

        return ComposedGlyph(
            space=space,
            region=LabeledRegion(
                space=space,
                contours=contours,
                label=label
            ),
            sprites=sprites,
            sub_glyphs=sub_glyphs
        )

    def place_debug_overlay(self) -> List[Sprite]:
        overlay: List[Sprite] = []

        overlay += super().place_debug_overlay()
        for g in self.sub_glyphs:
            overlay += g.place_debug_overlay()
        
        return overlay
