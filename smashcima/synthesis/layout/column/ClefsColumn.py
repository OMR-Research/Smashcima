from smashcima.geometry.Point import Point
from smashcima.scene.semantic.Clef import Clef
from smashcima.scene.semantic.Score import Score
from smashcima.scene.visual.StaffVisual import StaffVisual
from smashcima.scene.Glyph import Glyph
from smashcima.scene.SmuflLabels import SmuflLabels
from smashcima.synthesis.GlyphSynthesizer import GlyphSynthesizer
from .ColumnBase import ColumnBase
from typing import List, Set
import random


class ClefsColumn(ColumnBase):
    def __post_init__(self) -> None:
        self.clefs: List[Clef] = []

        # this column should not be grown much, really
        self.flex_grow = 0.1

    def add_clef(self, clef: Clef, clef_glyph: Glyph):
        self.clefs.append(clef)
        self.add_glyph(clef_glyph)

    def _position_glyphs(self):
        for clef, clef_glyph in zip(self.clefs, self.glyphs):
            sl = self.get_staff_of_glyph(clef_glyph)

            pitch_position = Clef.clef_line_to_pitch_position(clef.line)

            clef_glyph.space.transform = sl.staff_coordinate_system.get_transform(
                pitch_position=pitch_position,
                time_position=self.time_position
            )


def synthesize_header_clefs(
    staves: List[StaffVisual],
    rng: random.Random,
    glyph_synthesizer: GlyphSynthesizer,
    score: Score,
    measure_index: int
) -> ClefsColumn:
    column = ClefsColumn(staves, rng.random())

    # verification logic
    handled_staves: Set[int] = set()

    # go through all the parts
    for part in score.parts:
        measure = part.measures[measure_index]
        event = measure.first_event

        # and all the clefs in the part
        # (applying to the first event of the measure we are rendering)
        for staff_number, clef in event.attributes.clefs.items():

            # get the proper stafflines instance
            staff_index = score.first_staff_index_of_part(part) \
                + (staff_number - 1)
            staff = staves[staff_index]

            # determine the glyph class
            label = SmuflLabels.clef_from_clef_sign(
                clef_sign=clef.sign,
                small=False
            ).value

            # synthesize the glyph
            glyph = glyph_synthesizer.synthesize_glyph_at(
                label=label,
                parent_space=staff.space,
                point=Point(0, 0) # glyph positioned later
            )
            column.add_clef(clef, glyph)

            # verification logic
            if staff_index in handled_staves:
                raise Exception(
                    f"The staff {staff_index} had a clef be created twice!"
                )
            handled_staves.add(staff_index)
    
    # verify there is one clef for each staff
    assert len(handled_staves) == len(staves), \
        "All staves must get a clef when synthesizing the header clefs."
    
    return column


def synthesize_change_clefs() -> ClefsColumn:
    # TODO: synthesize clef changes (small clefs)
    pass
