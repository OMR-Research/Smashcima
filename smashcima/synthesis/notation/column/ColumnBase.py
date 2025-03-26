import abc
from typing import List
from .Column import Column
from smashcima.scene.visual.StaffVisual import StaffVisual
from smashcima.scene.Glyph import Glyph
from smashcima.scene.Sprite import Sprite
from smashcima.geometry.Vector2 import Vector2
from smashcima.geometry.Rectangle import Rectangle
import random


class ColumnBase(Column, metaclass=abc.ABCMeta):
    """Base class for layout columns that implements common logic,
    such as dimension calculation from glyph list"""
    def __init__(self, staves: List[StaffVisual], rng_seed: float):
        super().__init__()

        self.staves = staves
        "Reference to the list of stafflines we render onto"

        self.glyphs: List[Glyph] = []
        "Glyphs tracked in this column"

        self.rng_seed = rng_seed
        "Seed for the local RNG used for glyph positioning"

        self.rng = random.Random(self.rng_seed)
        "The RNG that should be used for randomizing glyph positioning"

        self.__post_init__()
    
    def __post_init__(self):
        # can be overriden in child classes
        pass
    
    def add_glyph(self, glyph: Glyph):
        """Adds a glyph into the column, the glyph must be in some staff space"""
        # check that the glyph is properly attached to stafflines
        self.get_staff_of_glyph(glyph)
        if glyph not in self.glyphs:
            self.glyphs.append(glyph)
    
    def get_staff_of_glyph(self, glyph: Glyph) -> StaffVisual:
        """Resolves the stafflines object for a given glyph"""
        for staff in self.staves:
            if staff.space is glyph.space.parent_space:
                return staff
        raise Exception(
            "Given glyph is not attached to any of the stafflines objects"
        )

    def position_glyphs(self):
        """Positions glyphs on staves according to the column's time position"""
        # reset RNG before any positioning
        self.rng = random.Random(self.rng_seed)
        self._position_glyphs()
        self.recalculate_dimensions()

    @abc.abstractmethod
    def _position_glyphs(self):
        """Glyph positioning implementation"""
        raise NotImplementedError

    def recalculate_dimensions(self):
        # reset all
        self.width = 0
        self.left_width = 0
        self.right_width = 0

        # map sprite corners to the stafflines space
        # relative to its time position
        points: List[Vector2] = []

        # for all staves
        for staff in self.staves:
            column_origin = staff.staff_coordinate_system.get_transform(
                0,
                self.time_position
            ).apply_to(Vector2(0, 0))

            # for all glyphs in that staff
            for glyph in self.glyphs:
                if glyph.space.parent_space is not staff.space:
                    continue

                # get all sprites in that glyph and transform their corners
                # into the staff space
                for (sprite, transform) in Sprite.traverse_sprites(
                    glyph.space,
                    include_pixels_transform=True,
                    include_sprite_transform=True,
                    include_root_space_transform=True
                ):
                    corners = [
                        transform.apply_to(Vector2(0, 0)),
                        transform.apply_to(Vector2(sprite.pixel_width, 0)),
                        transform.apply_to(Vector2(0, sprite.pixel_height)),
                        transform.apply_to(
                            Vector2(sprite.pixel_width, sprite.pixel_height)
                        )
                    ]
                    corners = [p - column_origin for p in corners]
                    points += corners

        # recalculate widths
        if len(points) > 0:
            self.left_width = -min(p.x for p in points)
            self.right_width = max(p.x for p in points)
            self.width = self.left_width + self.right_width
    
    def detach(self):
        for glyph in self.glyphs:
            glyph.detach()

    def place_debug_boxes(self):
        """For debugging purposes - places sprites that visualize the column"""
        for staff in self.staves:
            topleft = staff.staff_coordinate_system.get_transform(
                pitch_position=4,
                time_position=self.time_position - self.left_width
            ).apply_to(Vector2(0, 0))
            bottomright = staff.staff_coordinate_system.get_transform(
                pitch_position=-4,
                time_position=self.time_position + self.right_width
            ).apply_to(Vector2(0, 0))
            Sprite.debug_box(
                space=staff.space,
                rectangle=Rectangle(
                    x=topleft.x,
                    y=topleft.y,
                    width=bottomright.x - topleft.x,
                    height=bottomright.y - topleft.y
                ),
                fill_color=(0, 0, 0, 0),
                border_width=0.2 # mm
            )
