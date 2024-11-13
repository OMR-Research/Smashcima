from smashcima.scene.semantic.Score import Score
from smashcima.scene.semantic.ScoreEvent import ScoreEvent
from smashcima.scene.semantic.Note import Note
from smashcima.scene.semantic.Rest import Rest
from smashcima.scene.semantic.Durable import Durable
from smashcima.scene.visual.Stafflines import Stafflines
from smashcima.scene.visual.Accidental import Accidental
from smashcima.scene.visual.Notehead import Notehead
from smashcima.scene.visual.RestGlyph import RestGlyph
from smashcima.scene.SmuflLabels import SmuflLabels
from smashcima.synthesis.glyph.GlyphSynthesizer import GlyphSynthesizer
from smashcima.geometry.Point import Point
from smashcima.random_between import random_between
from .ColumnBase import ColumnBase
from .Skyline import Skyline
from typing import List, Dict, Optional, Union, Optional


class AccidentalsColumn(ColumnBase):
    def __post_init__(self):
        self.accidentals: List[Accidental] = []
    
    def add_accidental(self, accidental: Accidental):
        assert accidental.notehead is not None
        self.glyphs.append(accidental)
        self.accidentals.append(accidental)

    def _position_glyphs(self):
        self.place_accidentals()

    def place_accidentals(self):
        for stafflines in self.staves:
            self.place_accidentals_for_stafflines(stafflines)

    def place_accidentals_for_stafflines(self, stafflines: Stafflines):
        # extract all accidentals in this staff
        accidentals: List[Accidental] = []
        for accidental in self.accidentals:
            if self.get_stafflines_of_glyph(accidental.notehead) is not stafflines:
                continue
            accidentals.append(accidental)
        
        # extract all noteheads in this staff
        noteheads: List[Notehead] = []
        for glyph in self.glyphs:
            if not isinstance(glyph, Notehead):
                continue
            if self.get_stafflines_of_glyph(glyph) is not stafflines:
                continue
            noteheads.append(glyph)

        # constants
        SPACING = random_between(0.2, 1.0, self.rng) # between accidentals
        
        # where is the column in the staff space coords
        origin_x = stafflines.staff_coordinate_system.get_transform(
            0, self.time_position
        ).apply_to(Point(0, 0)).x

        # define the skyline by noteheads
        # (in the column-local space increasing to the right)
        skyline = Skyline(ground_level=0)
        for notehead in noteheads:
            bbox_global = notehead.get_bbox_in_space(stafflines.space)
            skyline.overlay_box(
                minimum=bbox_global.top,
                maximum=bbox_global.bottom,
                level=(origin_x - bbox_global.left)
            )

        # place accidentals
        for accidental in accidentals:
            assert accidental.notehead in noteheads, \
                "Not all noteheads have been extracted to build the skyline base"

            bbox_global = accidental.get_bbox_in_space(stafflines.space)
            bbox_local = accidental.get_bbox_in_space(accidental.space)

            skyline_left = skyline.drop_box(
                minimum=bbox_global.top,
                maximum=bbox_global.bottom,
                thickness=bbox_global.width + SPACING
            )
            accidental.space.transform = stafflines.staff_coordinate_system \
                .get_transform(
                    pitch_position=accidental.notehead.pitch_position,
                    time_position=(
                        self.time_position - bbox_local.left - skyline_left
                    )
                )

def synthesize_accidentals_column(
    column: AccidentalsColumn,
    staves: List[Stafflines],
    glyph_synthesizer: GlyphSynthesizer,
    score: Score,
    score_event: ScoreEvent
):
    for event in score_event.events:
        for durable in event.durables:
            if not isinstance(durable, Note):
                continue
            note = durable

            # skip notes with no accidental
            if note.accidental_value is None:
                continue

            # create accidental
            accidental = glyph_synthesizer.synthesize_glyph(
                glyph_class=SmuflLabels.accidental_from_accidental_value(
                    note.accidental_value
                ).value,
                expected_glyph_type=Accidental
            )
            accidental.notehead = Notehead.of_note(note, fail_if_none=True)
            stafflines_index = score.staff_index_of_durable(note)
            accidental.space.parent_space = staves[stafflines_index].space

            column.add_accidental(accidental)
