from smashcima.scene.visual.StaffVisual import StaffVisual
from smashcima.scene.visual.StaffCoordinateSystem import StaffCoordinateSystem
from smashcima.scene.AffineSpace import AffineSpace
from smashcima.scene.Sprite import Sprite
from smashcima.geometry.Vector2 import Vector2
from smashcima.geometry.Rectangle import Rectangle
from smashcima.geometry.Transform import Transform
from smashcima.geometry.units import px_to_mm
from .StafflinesSynthesizer import StafflinesSynthesizer


MUSCIMA_LINE_WIDTH = px_to_mm(1.5, dpi=300)
MUSCIMA_STAFF_SPACE = px_to_mm(28.75, dpi=300)


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
        self.staff_space: float = MUSCIMA_STAFF_SPACE
        self.line_width: float = MUSCIMA_LINE_WIDTH

    @property
    def staff_height(self) -> float:
        return self.staff_space * 4
    
    def synthesize_stafflines(
        self,
        parent_space: AffineSpace,
        position: Vector2,
        width: float
    ) -> StaffVisual:
        local_space = AffineSpace(
            parent_space=parent_space,
            transform=Transform.translate(position)
        )
        sprites = [
            Sprite.rectangle(
                local_space,
                Rectangle(
                    x=0,
                    y=i * self.staff_space - self.line_width / 2,
                    width=width,
                    height=self.line_width
                ),
                fill_color=(0, 0, 0, 255),
                dpi=300
            )
            for i in range(-2, 3)
        ]
        return StaffVisual(
            width=width,
            space=local_space,
            sprites=sprites,
            staff_coordinate_system=NaiveStaffCoordinateSystem(
                staff_space=self.staff_space
            )
        )
