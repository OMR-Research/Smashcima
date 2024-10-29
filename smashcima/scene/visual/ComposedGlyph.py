from dataclasses import dataclass, field
from ..Sprite import Sprite
from smashcima.geometry.Polygon import Polygon
from .Glyph import Glyph
from dataclasses import dataclass, field
from typing import List
import numpy as np


@dataclass
class ComposedGlyph(Glyph):
    """
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
    
    sub_glyphs: List[Glyph] = field(default_factory=list)
    "Glyphs that make up this larger glyph."

    def aggregate_sprites(self):
        """Sets the sprites field to a union of all child sprites"""
        self.sprites = []
        for g in self.sub_glyphs:
            self.sprites = [*self.sprites, *g.sprites]
    
    def get_contours(self) -> List[Polygon]:
        contours: List[Polygon] = []

        contours += Glyph.get_contours(self)
        for g in self.sub_glyphs:
            transform = self.space.transform_from(g.space)
            contours += [transform.apply_to(p) for p in g.get_contours()]
        
        return contours
    
    def place_debug_overlay(self) -> List[Sprite]:
        overlay: List[Sprite] = []

        overlay += Glyph.place_debug_overlay(self)
        for g in self.sub_glyphs:
            overlay += g.place_debug_overlay()
        
        return overlay
