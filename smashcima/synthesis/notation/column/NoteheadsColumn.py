from smashcima.scene.SmashcimaLabels import SmashcimaLabels
from smashcima.scene.semantic.Score import Score
from smashcima.scene.semantic.Event import Event
from smashcima.scene.semantic.StaffSemantic import StaffSemantic
from smashcima.scene.semantic.Chord import Chord
from smashcima.scene.semantic.StemValue import StemValue
from smashcima.scene.semantic.ScoreEvent import ScoreEvent
from smashcima.scene.semantic.Note import Note
from smashcima.scene.visual.StaffVisual import StaffVisual
from smashcima.scene.visual.Notehead import Notehead
from smashcima.scene.visual.NoteheadSide import NoteheadSide
from smashcima.scene.visual.LedgerLine import LegerLine
from smashcima.scene.SmuflLabels import SmuflLabels
from smashcima.synthesis.GlyphSynthesizer import GlyphSynthesizer
from smashcima.synthesis.LineSynthesizer import LineSynthesizer
from smashcima.geometry.Point import Point
from smashcima.random_between import random_between
from .ColumnBase import ColumnBase
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


# Notehead alignment
# ------------------
# There are 3 columns of noteheads, the center one is the default one and
# if a stem is pointing up, it's placed right of it; if down, it's placed
# left. If there is a one-tone step between two notes, then one of the noteheads
# kicks off to one of the side columns. Which direction it's kicked off depends
# on the stem direction, because the note has to kick off on the other side
# of the stem.


@dataclass
class _NoteheadContext:
    notehead: Notehead
    "The notehead"
    
    note: Note
    "A representative note of that notehead (WLOG the first one)"

    kick_asif_stem_up: bool
    "Perform kick off to the right, else to the left"

    kick_off: int = 0
    "Horizontal notehead column position: -1, 0, +1 for the three columns"


class NoteheadsColumn(ColumnBase):
    def __post_init__(self) -> None:
        self.notehead_contexts: List[_NoteheadContext] = []
        self.leger_lines: List[LegerLine] = []
    
    def set_line_synthesizer(self, line_synthesizer: LineSynthesizer):
        self.line_synthesizer = line_synthesizer

    def add_notehead(self, notehead: Notehead):
        assert len(notehead.notes) > 0

        self.glyphs.append(notehead.glyph)
        
        note = notehead.notes[0]
        chord = Chord.of_note(note)

        if chord.stem_value == StemValue.up:
            kick_asif_stem_up = True
        elif chord.stem_value == StemValue.down:
            kick_asif_stem_up = False
        elif chord.stem_value == StemValue.none \
                or chord.stem_value is None: # whole notes or unknown
            kick_asif_stem_up = True # assume invisible up-stem
        else:
            raise Exception(f"Unexpected stem value: {chord.stem_value}")

        self.notehead_contexts.append(_NoteheadContext(
            notehead=notehead,
            note=note,
            kick_asif_stem_up=kick_asif_stem_up
        ))
    
    def _position_glyphs(self):
        # noteheads
        for staff in self.staves:
            self.kick_off_noteheads_on_staff(staff)
        self.position_noteheads()
        
        # leger lines
        self.delete_current_leger_lines()
        for staff in self.staves:
            self.place_leger_lines(staff)

    def kick_off_noteheads_on_staff(self, staff: StaffVisual):
        contexts = [
            c for c in self.notehead_contexts
            if c.notehead.staff is staff
        ]
        contexts.sort(key=lambda c: c.note.pitch.get_linear_pitch())
        
        # lets go from bottom up and kick notes off the center line
        last_linear_pitch = -2
        last_was_kicked_off = True
        for ctx in contexts:
            linear_pitch = ctx.note.pitch.get_linear_pitch()

            # reset kick off
            ctx.kick_off = 0
            ctx.notehead.up_stem_attachment_side = NoteheadSide.right
            ctx.notehead.down_stem_attachment_side = NoteheadSide.left

            # if the previous pitch was kicked off,
            # then the current does not need to be
            if last_was_kicked_off:
                last_was_kicked_off = False
                last_linear_pitch = linear_pitch
                continue

            # ok, now if we have enough space, we also don't need to kick off
            if abs(linear_pitch - last_linear_pitch) >= 2:
                last_was_kicked_off = False
                last_linear_pitch = linear_pitch
                continue

            # now we are definitely tight, we need to kick off
            # just we need to figure out the direction
            last_was_kicked_off = True
            last_linear_pitch = linear_pitch

            if ctx.kick_asif_stem_up:
                ctx.kick_off = 1
                ctx.notehead.up_stem_attachment_side = NoteheadSide.left
                ctx.notehead.down_stem_attachment_side = None
            else:
                ctx.kick_off = -1
                ctx.notehead.up_stem_attachment_side = None
                ctx.notehead.down_stem_attachment_side = NoteheadSide.right

            ctx.kick_off = 1 if ctx.kick_asif_stem_up else -1
        
    def position_noteheads(self):
        if len(self.notehead_contexts) == 0:
            return
        
        center_notehead_stack_width = sum(
            ctx.notehead.glyph.get_bbox_in_space(ctx.notehead.staff.space).width
            for ctx in self.notehead_contexts
        ) / len(self.notehead_contexts) # average
        kick_off_distance = center_notehead_stack_width \
            * 1.2 # scale up a little to accomodate the stem

        for ctx in self.notehead_contexts:
            notehead = ctx.notehead
            sl = ctx.notehead.staff

            notehead.glyph.space.transform = sl.staff_coordinate_system.get_transform(
                pitch_position=ctx.notehead.pitch_position,
                time_position=self.time_position \
                    + (ctx.kick_off * kick_off_distance)
            )
    
    def place_leger_lines(self, staff: StaffVisual):
        contexts = [
            c for c in self.notehead_contexts
            if c.notehead.staff is staff
        ]

        if len(contexts) == 0:
            return
        
        def _leger_line_temporal_bounds(
            ctx: _NoteheadContext
        ) -> Tuple[float, float]:
            """Gets the time position of the two start and end of a basic
            leger line for a given (already placed) notehead"""
            bbox = ctx.notehead.glyph.get_bbox_in_space(ctx.notehead.staff.space)
            pos_x = ctx.notehead.staff.staff_coordinate_system.get_transform(
                pitch_position=0, time_position=self.time_position
            ).apply_to(Point(0, 0)).x
            center = self.time_position + (bbox.center.x - pos_x)
            
            # determine the leger line width
            # TODO: get from some distribution
            width = bbox.width * random_between(1.2, 2.5, self.rng)
            
            start = center - width / 2
            end = center + width / 2
            return start, end
        
        max_abs_pitch_position = max(
            abs(ctx.notehead.pitch_position) for ctx in contexts
        )

        # top-down, then bottom-up
        for sign in [1, -1]:
            affected_noteheads: List[Notehead] = []
            time_position_start = float("inf")
            time_position_end = float("-inf")

            # walk pitches towards staff center
            # (code is written for going top-down, then inverted by the sign)
            STAFF_EDGE_PP = 4
            for pitch_position in range(
                max_abs_pitch_position * sign, # start
                STAFF_EDGE_PP * sign, # stop (exclusive)
                -1 * sign # step
            ):
                # expand affected noteheads by the current noteheads
                for ctx in contexts:
                    if ctx.notehead.pitch_position == pitch_position:
                        affected_noteheads.append(ctx.notehead)
                        start, end = _leger_line_temporal_bounds(ctx)
                        time_position_start = min(time_position_start, start)
                        time_position_end = max(time_position_end, end)
                
                # create leger line
                # (if on even position and if we have some affected noteheads)
                if pitch_position % 2 == 0 and len(affected_noteheads) > 0:
                    line = self.synthesize_leger_line(
                        staff,
                        pitch_position=pitch_position,
                        time_position_start=time_position_start,
                        time_position_end=time_position_end
                    )
                    line.affected_noteheads = [*affected_noteheads] # copy
    
    def delete_current_leger_lines(self):
        for line in self.leger_lines:
            self.glyphs.remove(line.glyph)
            line.detach()
        self.leger_lines = []
    
    def synthesize_leger_line(
        self,
        staff: StaffVisual,
        pitch_position: int,
        time_position_start: float,
        time_position_end: float
    ) -> LegerLine:
        start_point = staff.staff_coordinate_system.get_transform(
            pitch_position=pitch_position,
            time_position=time_position_start
        ).apply_to(Point(0, 0))

        end_point = staff.staff_coordinate_system.get_transform(
            pitch_position=pitch_position,
            time_position=time_position_end
        ).apply_to(Point(0, 0))

        glyph = self.line_synthesizer.synthesize_line(
            label=SmashcimaLabels.legerLine.value,
            parent_space=staff.space,
            start_point=start_point,
            end_point=end_point
        )
        line = LegerLine(
            glyph=glyph,
            affected_noteheads=[], # populated later
            affected_rest=None
        )

        self.glyphs.append(glyph)
        self.leger_lines.append(line)

        return line
    
    def detach(self):
        super().detach()
        for ctx in self.notehead_contexts:
            ctx.notehead.detach()
        for l in self.leger_lines:
            l.detach()


def synthesize_noteheads_column(
    column: NoteheadsColumn,
    staves: List[StaffVisual],
    glyph_synthesizer: GlyphSynthesizer,
    line_synthesizer: LineSynthesizer,
    score: Score,
    score_event: ScoreEvent
):
    column.set_line_synthesizer(line_synthesizer)
    
    # notehead merging logic
    # (when two voices share a notehead)
    _all_noteheads: Dict[Tuple[int, int], Notehead] = dict()
    
    def _get_notehead(note: Note, staff_index: int) -> Optional[Notehead]:
        nonlocal _all_noteheads
        linear_pitch = note.pitch.get_linear_pitch()
        return _all_noteheads.get((staff_index, linear_pitch))

    def _store_notehead(note: Note, staff_index: int, notehead: Notehead):
        nonlocal _all_noteheads
        linear_pitch = note.pitch.get_linear_pitch()
        _all_noteheads[(staff_index, linear_pitch)] = notehead

    # go through all the notes and create notehead glyphs
    for event in score_event.events:
        for durable in event.durables:
            if isinstance(durable, Note):
                note: Note = durable
                staff_index = score.staff_index_of_durable(note)
                notehead = _get_notehead(note, staff_index)

                # another note for an existing notehead
                if notehead is not None:
                    notehead.notes = [*notehead.notes, note]
                    continue

                # resolve context
                event = Event.of_durable(note)
                staff_sem = StaffSemantic.of_durable(note)
                clef = event.attributes.clefs[staff_sem.staff_number]
                staff = staves[staff_index]
                
                # new notehead for a note
                glyph = glyph_synthesizer.synthesize_glyph_at(
                    label=SmuflLabels.notehead_from_type_duration(
                        note.type_duration
                    ).value,
                    parent_space=staff.space,
                    point=Point(0, 0) # glyph positioned later
                )
                notehead = Notehead(
                    glyph=glyph,
                    notes = [note],
                    clef=clef,
                    staff=staff,
                    pitch_position=clef.pitch_to_pitch_position(note.pitch),
                )
                _store_notehead(note, staff_index, notehead)
    
    # add noteheads to the column
    for notehead in _all_noteheads.values():
        column.add_notehead(notehead)
