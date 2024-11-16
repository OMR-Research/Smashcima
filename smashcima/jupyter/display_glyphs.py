from smashcima.geometry import Vector2
from smashcima.scene import Glyph, Sprite
import matplotlib.pyplot as plt
from typing import List
import cv2


def _plot_glyph_on_axis(ax: plt.Axes, glyph: Glyph, glyph_index: int):
    ax.set_title(str(glyph_index))

    for sprite, transform in Sprite.traverse_sprites(glyph.space):
        # upper left image corner
        a = transform.apply_to(Vector2(0, 0))

        # lower right image corner
        b = transform.apply_to(Vector2(sprite.pixel_width, sprite.pixel_height))

        # NOTE: this rendering does not support rotations!
        ax.imshow(
            cv2.cvtColor(sprite.bitmap, cv2.COLOR_BGRA2RGBA),
            extent=(a.x, b.x, b.y, a.y) # (left, right, bottom, top)
        )

        ax.plot([0.0], [0.0], "rx", alpha=0.8)


def display_glyphs(rows: int, columns: int, glyphs: List[Glyph], start_from=0):
    fig, axs = plt.subplots(rows, columns, sharex=True, sharey=True)
    fig.suptitle(glyphs[0].label + f" ({len(glyphs)} total)")
    fig.tight_layout()
    
    for r in range(rows):
        for c in range(columns):
            i = start_from + r * columns + c
            if i >= len(glyphs):
                continue
            _plot_glyph_on_axis(axs[r, c], glyphs[i], i)