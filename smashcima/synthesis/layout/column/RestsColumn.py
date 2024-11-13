from smashcima.scene import LineGlyph, SmashcimaLabels
from smashcima.scene.Glyph import Glyph
from smashcima.scene.semantic.Score import Score
from smashcima.scene.semantic.Event import Event
from smashcima.scene.semantic.Staff import Staff
from smashcima.scene.semantic.ScoreEvent import ScoreEvent
from smashcima.scene.semantic.Rest import Rest
from smashcima.scene.visual.Stafflines import Stafflines
from smashcima.scene.visual.RestGlyph import RestGlyph
from smashcima.scene.visual.LedgerLine import LedgerLine
from smashcima.scene.SmuflLabels import SmuflLabels
from smashcima.synthesis.glyph.GlyphSynthesizer import GlyphSynthesizer
from smashcima.synthesis.glyph.LineSynthesizer import LineSynthesizer
from smashcima.geometry.Point import Point
from smashcima.random_between import random_between
from .ColumnBase import ColumnBase
from typing import List
import random


class RestsColumn(ColumnBase):
    def __post_init__(self) -> None:
        self.rest_glyphs: List[RestGlyph] = []

    def add_rest(self, rest_glyph: RestGlyph):
        assert rest_glyph.rest is not None
        self.glyphs.append(rest_glyph.glyph)
        self.rest_glyphs.append(rest_glyph)
    
    def _position_glyphs(self):
        self.position_rests()
    
    def position_rests(self):
        for rest_glyph in self.rest_glyphs:
            display_pitch = rest_glyph.rest.display_pitch \
                or RestGlyph.default_display_pitch(
                    rest_glyph.clef, rest_glyph.rest.type_duration
                )
            pitch_position = RestGlyph.display_pitch_to_glyph_pitch_position(
                rest_glyph.clef, display_pitch, rest_glyph.rest.type_duration
            )

            rest_glyph.glyph.space.transform = rest_glyph.stafflines.staff_coordinate_system \
                .get_transform(
                    pitch_position=pitch_position,
                    time_position=self.time_position
                )


def synthesize_rests_column(
    column: RestsColumn,
    staves: List[Stafflines],
    glyph_synthesizer: GlyphSynthesizer,
    line_synthesizer: LineSynthesizer,
    score: Score,
    score_event: ScoreEvent,
    rng: random.Random
):
    # for all the rests (including measure rests)
    for event in score_event.events:
        for durable in event.durables:
            if not isinstance(durable, Rest): # inlcudes MeasureRest
                continue
            
            # resolve context
            event = Event.of_durable(durable, fail_if_none=True)
            staff = Staff.of_durable(durable, fail_if_none=True)
            clef = event.attributes.clefs[staff.staff_number]
            stafflines_index = score.staff_index_of_durable(durable)
            stafflines = staves[stafflines_index]

            # resolve pitch position
            display_pitch = durable.display_pitch \
                or RestGlyph.default_display_pitch(
                    clef, durable.type_duration
                )
            pitch_position = RestGlyph.display_pitch_to_glyph_pitch_position(
                clef, display_pitch, durable.type_duration
            )

            # create the rest
            glyph_class = SmuflLabels.rest_from_type_duration(
                durable.type_duration
            )
            glyph = glyph_synthesizer.synthesize_glyph(
                glyph_class.value,
                expected_glyph_type=Glyph
            )
            glyph.space.parent_space = stafflines.space
            rest_glyph = RestGlyph(
                glyph=glyph,
                rest = durable,
                clef = clef,
                stafflines = stafflines,
                pitch_position = pitch_position,
            )
            column.add_rest(rest_glyph)

            # create ledger line for whole/half rests
            # (and attach it under the glyph space for simplicity)
            _synthesize_ledger_line_if_necessary(
                rest_glyph=rest_glyph,
                glyph_class=glyph_class,
                line_synthesizer=line_synthesizer,
                rng=rng
            )


def _synthesize_ledger_line_if_necessary(
    rest_glyph: RestGlyph,
    glyph_class: SmuflLabels,
    line_synthesizer: LineSynthesizer,
    rng: random.Random
):
    # the rest is not whole nor half, no ledger line needed
    if glyph_class not in [SmuflLabels.restWhole, SmuflLabels.restHalf]:
        return

    # the rest is still within the staff, no ledgerline needed
    if abs(rest_glyph.pitch_position) < 4:
        return

    width = rest_glyph.glyph.get_bbox_in_space(rest_glyph.glyph.space).width \
        * random_between(1.2, 2.5, rng)
    
    glyph = line_synthesizer.synthesize_line(
        glyph_type=LineGlyph,
        glyph_class=SmashcimaLabels.ledgerLine.value,
        start_point=Point(-width / 2, 0),
        end_point=Point(width / 2, 0)
    )
    glyph.space.parent_space = rest_glyph.glyph.space
    LedgerLine(
        glyph=glyph,
        affected_noteheads=[], # none
        affected_rest = rest_glyph
    )
