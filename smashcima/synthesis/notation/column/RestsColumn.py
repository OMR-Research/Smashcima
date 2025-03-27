from smashcima.scene import SmashcimaLabels
from smashcima.scene.semantic.Score import Score
from smashcima.scene.semantic.Event import Event
from smashcima.scene.semantic.StaffSemantic import StaffSemantic
from smashcima.scene.semantic.ScoreEvent import ScoreEvent
from smashcima.scene.semantic.RestSemantic import RestSemantic
from smashcima.scene.visual.StaffVisual import StaffVisual
from smashcima.scene.visual.RestVisual import RestVisual
from smashcima.scene.visual.LedgerLine import LegerLine
from smashcima.scene.SmuflLabels import SmuflLabels
from smashcima.synthesis.GlyphSynthesizer import GlyphSynthesizer
from smashcima.synthesis.LineSynthesizer import LineSynthesizer
from smashcima.geometry.Point import Point
from smashcima.random_between import random_between
from .ColumnBase import ColumnBase
from typing import List
import random


class RestsColumn(ColumnBase):
    def __post_init__(self) -> None:
        self.rests: List[RestVisual] = []

    def add_rest(self, rest_glyph: RestVisual):
        assert rest_glyph.rest_semantic is not None
        self.glyphs.append(rest_glyph.glyph)
        self.rests.append(rest_glyph)
    
    def _position_glyphs(self):
        self.position_rests()
    
    def position_rests(self):
        for rest in self.rests:
            display_pitch = rest.rest_semantic.display_pitch \
                or RestVisual.default_display_pitch(
                    rest.clef, rest.rest_semantic.type_duration
                )
            pitch_position = RestVisual.display_pitch_to_glyph_pitch_position(
                rest.clef, display_pitch, rest.rest_semantic.type_duration
            )

            rest.glyph.space.transform = rest.staff.staff_coordinate_system \
                .get_transform(
                    pitch_position=pitch_position,
                    time_position=self.time_position
                )
    
    def detach(self):
        super().detach()
        for rest in self.rests:
            rest.detach()


def synthesize_rests_column(
    column: RestsColumn,
    staves: List[StaffVisual],
    glyph_synthesizer: GlyphSynthesizer,
    line_synthesizer: LineSynthesizer,
    score: Score,
    score_event: ScoreEvent,
    rng: random.Random
):
    # for all the rests (including measure rests)
    for event in score_event.events:
        for durable in event.durables:
            if not isinstance(durable, RestSemantic): # inlcudes MeasureRest
                continue
            
            # resolve context
            event = Event.of_durable(durable)
            staff_sem = StaffSemantic.of_durable(durable)
            clef = event.attributes.clefs[staff_sem.staff_number]
            staff_index = score.staff_index_of_durable(durable)
            staff = staves[staff_index]

            # resolve pitch position
            display_pitch = durable.display_pitch \
                or RestVisual.default_display_pitch(
                    clef, durable.type_duration
                )
            pitch_position = RestVisual.display_pitch_to_glyph_pitch_position(
                clef, display_pitch, durable.type_duration
            )

            # create the rest
            label = SmuflLabels.rest_from_type_duration(
                durable.type_duration
            )
            glyph = glyph_synthesizer.synthesize_glyph_at(
                label=label.value,
                parent_space=staff.space,
                point=Point(0, 0) # glyph positioned later
            )
            rest = RestVisual(
                glyph=glyph,
                rest_semantic=durable,
                clef=clef,
                staff=staff,
                pitch_position=pitch_position,
            )
            column.add_rest(rest)

            # create leger line for whole/half rests
            # (and attach it under the glyph space for simplicity)
            _synthesize_leger_line_if_necessary(
                rest=rest,
                label=label,
                line_synthesizer=line_synthesizer,
                rng=rng
            )


def _synthesize_leger_line_if_necessary(
    rest: RestVisual,
    label: SmuflLabels,
    line_synthesizer: LineSynthesizer,
    rng: random.Random
):
    # the rest is not whole nor half, no leger line needed
    if label not in [SmuflLabels.restWhole, SmuflLabels.restHalf]:
        return

    # the rest is still within the staff, no legerline needed
    if abs(rest.pitch_position) < 4:
        return

    width = rest.glyph.get_bbox_in_space(rest.glyph.space).width \
        * random_between(1.2, 2.5, rng)
    
    glyph = line_synthesizer.synthesize_line(
        label=SmashcimaLabels.legerLine.value,
        parent_space=rest.glyph.space,
        start_point=Point(-width / 2, 0),
        end_point=Point(width / 2, 0)
    )
    LegerLine(
        glyph=glyph,
        affected_noteheads=[], # none
        affected_rest=rest
    )
