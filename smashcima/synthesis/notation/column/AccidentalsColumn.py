from smashcima.scene.semantic.Score import Score
from smashcima.scene.semantic.ScoreEvent import ScoreEvent
from smashcima.scene.semantic.Note import Note
from smashcima.scene.visual.StaffVisual import StaffVisual
from smashcima.scene.visual.Accidental import Accidental
from smashcima.scene.visual.Notehead import Notehead
from smashcima.scene.SmuflLabels import SmuflLabels
from smashcima.synthesis.GlyphSynthesizer import GlyphSynthesizer
from smashcima.geometry.Point import Point
from smashcima.random_between import random_between
from .ColumnBase import ColumnBase
from .Skyline import Skyline
from typing import List


class AccidentalsColumn(ColumnBase):
    def __post_init__(self) -> None:
        self.accidentals: List[Accidental] = []
    
    def add_accidental(self, accidental: Accidental):
        assert accidental.notehead is not None
        self.glyphs.append(accidental.glyph)
        self.accidentals.append(accidental)

    def _position_glyphs(self):
        self.place_accidentals()

    def place_accidentals(self):
        for staff in self.staves:
            self.place_accidentals_for_staff(staff)

    def place_accidentals_for_staff(self, staff: StaffVisual):
        # extract all accidentals in this staff
        accidentals: List[Accidental] = []
        for accidental in self.accidentals:
            if self.get_staff_of_glyph(accidental.notehead.glyph) is not staff:
                continue
            accidentals.append(accidental)
        
        # extract all noteheads in this staff
        # TODO: this is ugly, it's crawling the graph in ways it should not
        noteheads: List[Notehead] = []
        for glyph in self.glyphs:
            notehead = Notehead.of_or_none(glyph, lambda n: n.glyph)
            if notehead is None:
                continue
            if self.get_staff_of_glyph(glyph) is not staff:
                continue
            noteheads.append(notehead)

        # constants
        SPACING = random_between(0.2, 1.0, self.rng) # between accidentals
        
        # where is the column in the staff space coords
        origin_x = staff.staff_coordinate_system.get_transform(
            0, self.time_position
        ).apply_to(Point(0, 0)).x

        # define the skyline by noteheads
        # (in the column-local space increasing to the right)
        skyline = Skyline(ground_level=0)
        for notehead in noteheads:
            bbox_global = notehead.glyph.get_bbox_in_space(staff.space)
            skyline.overlay_box(
                minimum=bbox_global.top,
                maximum=bbox_global.bottom,
                level=(origin_x - bbox_global.left)
            )

        # place accidentals
        for accidental in accidentals:
            assert accidental.notehead in noteheads, \
                "Not all noteheads have been extracted to build the skyline base"

            bbox_global = accidental.glyph.get_bbox_in_space(staff.space)
            bbox_local = accidental.glyph.get_bbox_in_space(accidental.glyph.space)

            skyline_left = skyline.drop_box(
                minimum=bbox_global.top,
                maximum=bbox_global.bottom,
                thickness=bbox_global.width + SPACING
            )
            accidental.glyph.space.transform = staff.staff_coordinate_system \
                .get_transform(
                    pitch_position=accidental.notehead.pitch_position,
                    time_position=(
                        self.time_position - bbox_local.left - skyline_left
                    )
                )
    
    def detach(self):
        super().detach()
        for a in self.accidentals:
            a.detach()

def synthesize_accidentals_column(
    column: AccidentalsColumn,
    staves: List[StaffVisual],
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
            staff_index = score.staff_index_of_durable(note)
            glyph = glyph_synthesizer.synthesize_glyph_at(
                label=SmuflLabels.accidental_from_accidental_value(
                    note.accidental_value
                ).value,
                parent_space=staves[staff_index].space,
                point=Point(0, 0) # glyph positioned later
            )
            accidental = Accidental(
                glyph=glyph,
                notehead=Notehead.of_note(note)
            )
            column.add_accidental(accidental)
