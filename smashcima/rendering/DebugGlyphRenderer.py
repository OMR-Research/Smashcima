from smashcima.scene.visual.Glyph import Glyph
from smashcima.scene.ViewBox import ViewBox
from smashcima.scene.Scene import Scene
from .BitmapRenderer import BitmapRenderer
import numpy as np
import copy


class DebugGlyphRenderer:
    """Rasterizer meant to render a single glyph with debug metadata overlay"""
    def render(self, glyph: Glyph) -> np.ndarray:
        glyph = copy.deepcopy(glyph) # make a copy and modify that
        
        # add sprites to display debug points
        glyph.place_debug_overlay()

        scene = Scene()
        glyph.space.parent_space = scene.root_space
        scene.add_closure()

        view_box = ViewBox(glyph.get_bbox_in_space(scene.root_space))
        dpi = max(s.dpi for s in glyph.sprites)

        renderer = BitmapRenderer(dpi=dpi)
        return renderer.render(scene, view_box)
