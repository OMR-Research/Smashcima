from smashcima.geometry.Point import Point
from smashcima.scene.visual.StaffVisual import StaffVisual
from smashcima.scene.Glyph import Glyph
from smashcima.scene.SmuflLabels import SmuflLabels
from smashcima.synthesis.GlyphSynthesizer import GlyphSynthesizer
from .ColumnBase import ColumnBase
from typing import List
import random


class BarlinesColumn(ColumnBase):
    # TODO: synthesize tall barlines for piano (multi-staff parts)

    def __post_init__(self):
        # this column should not be grown much, really
        self.flex_grow = 0.1

    def add_barline(self, barline: Glyph):
        self.add_glyph(barline)

    def _position_glyphs(self):
        for barline in self.glyphs:
            sl = self.get_staff_of_glyph(barline)

            barline.space.transform = sl.staff_coordinate_system.get_transform(
                pitch_position=0, # centered on the staff
                time_position=self.time_position
            )


def synthesize_barlines_column(
    staves: List[StaffVisual],
    rng: random.Random,
    glyph_synthesizer: GlyphSynthesizer
) -> BarlinesColumn:
    column = BarlinesColumn(staves, rng.random())

    for staff in staves:
        barline = glyph_synthesizer.synthesize_glyph_at(
            label=SmuflLabels.barlineSingle.value,
            parent_space=staff.space,
            point=Point(0, 0) # glyph positioned later
        )
        barline.space.parent_space = staff.space
        column.add_barline(barline)

    return column
