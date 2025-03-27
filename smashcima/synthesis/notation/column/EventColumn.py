from smashcima.scene.semantic.Score import Score
from smashcima.scene.semantic.ScoreEvent import ScoreEvent
from smashcima.scene.visual.StaffVisual import StaffVisual
from smashcima.synthesis.GlyphSynthesizer import GlyphSynthesizer
from smashcima.synthesis.LineSynthesizer import LineSynthesizer
from .NoteheadsColumn import NoteheadsColumn, synthesize_noteheads_column
from .RestsColumn import RestsColumn, synthesize_rests_column
from .ColumnBase import ColumnBase
from .AugmentationDotsColumn import AugmentationDotsColumn, \
    synthesize_augmentation_dots_column
from .AccidentalsColumn import AccidentalsColumn, synthesize_accidentals_column
from typing import List
import random


class EventColumn(
    NoteheadsColumn,
    RestsColumn,
    AugmentationDotsColumn,
    AccidentalsColumn
):
    def __init__(self, *args, **kwargs):
        # ignore constructors of parents, initialize only the super-parent
        ColumnBase.__init__(self, *args, **kwargs)
    
    def __post_init__(self):
        NoteheadsColumn.__post_init__(self)
        RestsColumn.__post_init__(self)
        AugmentationDotsColumn.__post_init__(self)
        AccidentalsColumn.__post_init__(self)

    def _position_glyphs(self):
        NoteheadsColumn._position_glyphs(self)
        RestsColumn._position_glyphs(self)
        AugmentationDotsColumn._position_glyphs(self)
        AccidentalsColumn._position_glyphs(self)
    
    def detach(self):
        # detach glyphs
        ColumnBase.detach(self)

        # detach visual scene objects that link to semantic objects
        NoteheadsColumn.detach(self)
        RestsColumn.detach(self)
        AugmentationDotsColumn.detach(self)
        AccidentalsColumn.detach(self)


def synthesize_event_column(
    staves: List[StaffVisual],
    rng: random.Random,
    glyph_synthesizer: GlyphSynthesizer,
    line_synthesizer: LineSynthesizer,
    score: Score,
    score_event: ScoreEvent
) -> EventColumn:
    column = EventColumn(staves, rng.random())

    synthesize_noteheads_column(
        column=column,
        staves=staves,
        glyph_synthesizer=glyph_synthesizer,
        line_synthesizer=line_synthesizer,
        score=score,
        score_event=score_event
    )

    synthesize_rests_column(
        column=column,
        staves=staves,
        glyph_synthesizer=glyph_synthesizer,
        line_synthesizer=line_synthesizer,
        score=score,
        score_event=score_event,
        rng=rng
    )

    synthesize_augmentation_dots_column(
        column=column,
        staves=staves,
        glyph_synthesizer=glyph_synthesizer,
        score=score,
        score_event=score_event
    )

    synthesize_accidentals_column(
        column=column,
        staves=staves,
        glyph_synthesizer=glyph_synthesizer,
        score=score,
        score_event=score_event
    )
    
    return column
