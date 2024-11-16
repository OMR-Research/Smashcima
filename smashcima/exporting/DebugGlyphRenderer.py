from smashcima.scene.AffineSpace import AffineSpace
from smashcima.scene.Glyph import Glyph
from smashcima.scene.ViewBox import ViewBox
from .BitmapRenderer import BitmapRenderer
import numpy as np
import copy


class DebugGlyphRenderer:
    """Rasterizer meant to render a single glyph with debug metadata overlay"""
    def render(self, glyph: Glyph) -> np.ndarray:
        glyph = copy.deepcopy(glyph) # make a copy and modify that
        
        # add sprites to display debug points
        glyph.place_debug_overlay()

        root_space = AffineSpace()
        glyph.space.parent_space = root_space

        view_box = ViewBox(
            rectangle=glyph.get_bbox_in_space(root_space),
            space=root_space
        )
        dpi = max(s.dpi for s in glyph.sprites)

        renderer = BitmapRenderer(dpi=dpi)
        return renderer.render(view_box)
