from smashcima.scene.semantic.Score import Score
from smashcima.scene.semantic.ScoreEvent import ScoreEvent
from smashcima.scene.semantic.Note import Note
from smashcima.scene.semantic.RestSemantic import RestSemantic
from smashcima.scene.semantic.Durable import Durable
from smashcima.scene.visual.StaffVisual import StaffVisual
from smashcima.scene.visual.AugmentationDot import AugmentationDot
from smashcima.scene.visual.Notehead import Notehead
from smashcima.scene.visual.RestVisual import RestVisual
from smashcima.scene.SmuflLabels import SmuflLabels
from smashcima.synthesis.GlyphSynthesizer import GlyphSynthesizer
from smashcima.geometry.Point import Point
from smashcima.random_between import random_between
from .ColumnBase import ColumnBase
from typing import List, Dict, Optional, Union


class AugmentationDotsColumn(ColumnBase):
    def __post_init__(self) -> None:
        self.augmentation_dots: List[AugmentationDot] = []
    
    def add_augmentation_dot(self, augmentation_dot: AugmentationDot):
        assert len(augmentation_dot.owners) > 0
        self.glyphs.append(augmentation_dot.glyph)
        self.augmentation_dots.append(augmentation_dot)

    def _position_glyphs(self):
        self.place_augmentation_dots()

    def place_augmentation_dots(self):
        for staff in self.staves:
            self.place_augmentation_dots_for_staff(staff)

    def place_augmentation_dots_for_staff(self, staff: StaffVisual):
        noteheads: List[Notehead] = []
        notehead_dots: List[AugmentationDot] = []
        rests: List[RestVisual] = []
        rest_dots: List[AugmentationDot] = []
        for dot in self.augmentation_dots:
            for owner in dot.owners:
                if self.get_staff_of_glyph(owner.glyph) is not staff:
                    continue # skip glyphs in other staves
                if isinstance(owner, Notehead):
                    noteheads.append(owner)
                    notehead_dots.append(dot)
                elif isinstance(owner, RestVisual):
                    rests.append(owner)
                    rest_dots.append(dot)
        
        # where is the column in the staff space coords
        origin_x = staff.staff_coordinate_system.get_transform(
            0, self.time_position
        ).apply_to(Point(0, 0)).x

        # get right edge of all noteheads
        noteheads_right_edge = origin_x
        for notehead in noteheads:
            r = notehead.glyph.get_bbox_in_space(staff.space).right
            noteheads_right_edge = max(noteheads_right_edge, r)
        
        # constants
        BASE_OFFSET = random_between(1.0, 2.0, self.rng) # only used for noteheads
        SPACING = random_between(0.8, 1.6, self.rng) # between dots

        # place notehead dots
        for dot in notehead_dots:
            position_x = BASE_OFFSET + SPACING * (dot.augmentation_dot_index - 1)
            time_position = self.time_position + (
                noteheads_right_edge - origin_x
            ) + position_x
            dot.glyph.space.transform = staff.staff_coordinate_system.get_transform(
                pitch_position=dot.pitch_position,
                time_position=time_position
            )
        
        # place rest dots
        for dot in rest_dots:
            rest_right_edge = dot.owners[0].glyph.get_bbox_in_space(
                staff.space
            ).right
            position_x = SPACING * dot.augmentation_dot_index
            time_position = self.time_position + (
                rest_right_edge - origin_x
            ) + position_x
            dot.glyph.space.transform = staff.staff_coordinate_system.get_transform(
                pitch_position=dot.pitch_position,
                time_position=time_position
            )
    
    def detach(self):
        super().detach()
        for d in self.augmentation_dots:
            d.detach()

def synthesize_augmentation_dots_column(
    column: AugmentationDotsColumn,
    staves: List[StaffVisual],
    glyph_synthesizer: GlyphSynthesizer,
    score: Score,
    score_event: ScoreEvent
):
    # cluster durables by staff
    durables: Dict[int, List[Durable]] = {}
    for event in score_event.events:
        for durable in event.durables:
            staff_index = score.staff_index_of_durable(durable)
            durables.setdefault(staff_index, [])
            durables[staff_index].append(durable)

    # for each staff durables
    for staff_index, staffline_durables in durables.items():
        created_dots: Dict[int, List[AugmentationDot]] = dict() # by pitch pos
        handled_noteheads: List[Notehead] = []

        # sort by pitch from high-to-low
        # (in order for noteheads to properly distribute dots)
        sorted_durables = list(staffline_durables)
        sorted_durables.sort(key=lambda d:
            d.pitch.get_linear_pitch() if isinstance(d, Note) else 0,
            reverse=True
        )

        for durable in sorted_durables:
            owner: Union[None, Notehead, RestVisual] = None
            pitch_position: Optional[int] = None
            augmentation_dot_count: int = 0

            # handle noteheads
            if isinstance(durable, Note):
                notehead = Notehead.of_note(durable)
                if notehead in handled_noteheads:
                    continue
                handled_noteheads.append(notehead)

                owner = notehead
                pitch_position = notehead.pitch_position
                augmentation_dot_count = durable.augmentation_dots

            # handle rests
            elif isinstance(durable, RestSemantic):
                rest_glyph = RestVisual.of_rest(durable)
                owner = rest_glyph
                pitch_position = rest_glyph.pitch_position
                augmentation_dot_count = durable.augmentation_dots

            # skip other durables (there should be none)
            else:
                continue

            # skip noteheads with no dots
            if augmentation_dot_count == 0:
                continue

            # alter pitch position if we are placed on line
            if pitch_position % 2 == 0:
                # try moving up if not taken
                if (pitch_position + 1) not in created_dots:
                    pitch_position += 1
                # else down
                elif (pitch_position - 1) not in created_dots:
                    pitch_position -= 1
                # else just up and reuse the dots there
                else:
                    pitch_position += 1

            # for all duration dots
            created_dots.setdefault(pitch_position, [])
            dots: List[AugmentationDot] = created_dots[pitch_position]
            for dot_index in range(1, augmentation_dot_count + 1):

                # reuse existing dot
                if dot_index <= len(dots):
                    dot = dots[dot_index - 1]
                    assert dot.augmentation_dot_index == dot_index
                    assert dot.pitch_position == pitch_position
                    dot.owners = [*dot.owners, owner]

                # create new dot
                glyph = glyph_synthesizer.synthesize_glyph_at(
                    label=SmuflLabels.augmentationDot.value,
                    parent_space=staves[staff_index].space,
                    point=Point(0, 0) # glyph positioned later
                )
                dot = AugmentationDot(
                    glyph=glyph,
                    owners=[owner],
                    augmentation_dot_index=dot_index,
                    pitch_position=pitch_position,
                )
                dots.append(dot)

                column.add_augmentation_dot(dot)
