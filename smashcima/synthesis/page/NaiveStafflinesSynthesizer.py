from typing import List
from smashcima.geometry.Contours import Contours
from smashcima.geometry.Polygon import Polygon
from smashcima.scene.LabeledRegion import LabeledRegion
from smashcima.scene.SmashcimaLabels import SmashcimaLabels
from smashcima.scene.visual.StaffVisual import StaffVisual
from smashcima.scene.visual.StaffCoordinateSystem import StaffCoordinateSystem
from smashcima.scene.AffineSpace import AffineSpace
from smashcima.scene.Sprite import Sprite
from smashcima.scene.Glyph import Glyph
from smashcima.scene.ComposedGlyph import ComposedGlyph
from smashcima.geometry.Vector2 import Vector2
from smashcima.geometry.Rectangle import Rectangle
from smashcima.geometry.Transform import Transform
from smashcima.geometry.units import px_to_mm
from ..StafflinesSynthesizer import StafflinesSynthesizer


MUSCIMA_LINE_THICKNESS = px_to_mm(1.5, dpi=300)
MUSCIMA_STAFF_SPACE_UNIT = px_to_mm(28.75, dpi=300)


class NaiveStaffCoordinateSystem(StaffCoordinateSystem):
    def __init__(self, staff_space: float):
        self.staff_space = staff_space
    
    def get_transform(
        self,
        pitch_position: float,
        time_position: float
    ) -> Transform:
        return Transform.translate(
            Vector2(
                x=time_position,
                y=self.staff_space * (-pitch_position / 2)
            )
        )


class NaiveStafflinesSynthesizer(StafflinesSynthesizer):
    """Simple stafflines synthesizer that just creates straight stafflines"""
    def __init__(self) -> None:
        self.staff_space_unit: float = MUSCIMA_STAFF_SPACE_UNIT
        self.line_thickness: float = MUSCIMA_LINE_THICKNESS
        self.line_color = (0, 0, 0, 255)

    @property
    def staff_height(self) -> float:
        return self.staff_space_unit * 4
    
    def synthesize_stafflines(
        self,
        page_space: AffineSpace,
        position: Vector2,
        width: float
    ) -> StaffVisual:
        staff_space = AffineSpace(
            parent_space=page_space,
            transform=Transform.translate(position)
        )

        glyph = self.create_staff_glyph(staff_space, width)

        return StaffVisual(
            width=width,
            staff_coordinate_system=NaiveStaffCoordinateSystem(
                staff_space=self.staff_space_unit
            ),
            space=staff_space,
            glyph=glyph,
            staff_height=self.staff_height
        )
    
    def create_staff_glyph(
        self,
        staff_space: AffineSpace,
        width: float
    ) -> ComposedGlyph:
        sub_glyphs: List[Glyph] = []

        # create all staffline subglyphs
        for line_offset in range(-2, 3):
            line_space = AffineSpace()
            line_rectangle = Rectangle(
                x=0,
                y=line_offset * self.staff_space_unit - self.line_thickness / 2,
                width=width,
                height=self.line_thickness
            )
            line_sprite = Sprite.rectangle(
                line_space,
                line_rectangle,
                fill_color=self.line_color,
                dpi=300
            )
            sub_glyphs.append(Glyph(
                space=line_space,
                region=LabeledRegion(
                    space=line_space,
                    label=SmashcimaLabels.staffLine.value,
                    contours=Contours([
                        Polygon.from_rectangle(line_rectangle)
                    ])
                ),
                sprites=[line_sprite]
            ))
        
        # build the composed glyph
        composed_glyph = ComposedGlyph.build(
            label=SmashcimaLabels.staff.value,
            sub_glyphs=sub_glyphs
        )

        # attach the composed glyph under the staff space
        composed_glyph.space.parent_space = staff_space

        return composed_glyph
