from smashcima.scene.visual.Page import Page
from smashcima.scene.visual.StaffVisual import StaffVisual
from smashcima.geometry.Vector2 import Vector2
from smashcima.geometry.Rectangle import Rectangle
from smashcima.geometry.Transform import Transform
from smashcima.scene.ViewBox import ViewBox
from smashcima.scene.AffineSpace import AffineSpace
from smashcima.synthesis.PageSynthesizer import PageSynthesizer
from ..StafflinesSynthesizer import StafflinesSynthesizer
from ..PaperSynthesizer import PaperSynthesizer
from typing import List
from dataclasses import dataclass


@dataclass
class PageSetup:
    size: Vector2

    padding_top: float
    padding_bottom: float
    padding_left: float
    padding_right: float

    staff_count: int


HANDWRITTEN_PAGE_SETUP = PageSetup(
    # inspired by:
    # https://www.digitalniknihovna.cz/mzk/view/uuid:378147a5-3d3f-47f0-9f31-80740052e86c?page=uuid:74c8e808-1dd3-4ff7-bea5-658b7d4cb1a5
    size = Vector2(250, 350),
    padding_top=20,
    padding_bottom=40,
    padding_left=10,
    padding_right=10,
    staff_count=13
)


MUSESCORE_PAGE_SETUP = PageSetup(
    # A4 page with MuseScore-like padding
    size = Vector2(210, 297),
    padding_top=10,
    padding_bottom=10,
    padding_left=10,
    padding_right=10,
    staff_count=12
)


class SimplePageSynthesizer(PageSynthesizer):
    """Synthesizes page layout"""
    def __init__(
        self,
        stafflines_synthesizer: StafflinesSynthesizer,
        paper_synthesizer: PaperSynthesizer
    ):
        self.stafflines_synthesizer = stafflines_synthesizer
        self.paper_synthesizer = paper_synthesizer

        self.page_setup = MUSESCORE_PAGE_SETUP

    def synthesize_page(self, page_origin: Vector2) -> Page:
        page_space = AffineSpace(
            transform=Transform.translate(page_origin)
        )

        view_box = ViewBox(
            rectangle=Rectangle(
                page_origin.x,
                page_origin.y,
                self.page_setup.size.x,
                self.page_setup.size.y
            ),
            space=page_space
        )

        self.paper_synthesizer.synthesize_paper(
            page_space=page_space,
            placement=Rectangle(
                0, 0,
                self.page_setup.size.x,
                self.page_setup.size.y
            )
        )

        staves = self._synthesize_stafflines(page_space)

        return Page(
            space=page_space,
            view_box=view_box,
            staves=staves
        )
    
    def _synthesize_stafflines(self, page_space: AffineSpace) -> List[StaffVisual]:
        content_box = Rectangle(
            self.page_setup.padding_left,
            self.page_setup.padding_top,
            self.page_setup.size.x \
                - (self.page_setup.padding_left + self.page_setup.padding_right),
            self.page_setup.size.y \
                - (self.page_setup.padding_top + self.page_setup.padding_bottom)
        )

        starting_point = content_box.y \
            + self.stafflines_synthesizer.staff_height / 2

        vertical_step = (content_box.height \
            - self.stafflines_synthesizer.staff_height) \
            / (self.page_setup.staff_count - 1)

        staves: List[StaffVisual] = []
        for i in range(self.page_setup.staff_count):
            stafflines = self.stafflines_synthesizer.synthesize_stafflines(
                page_space=page_space,
                position=Vector2(
                    content_box.x,
                    starting_point + i * vertical_step
                ),
                width=content_box.width
            )
            staves.append(stafflines)
        
        return staves
