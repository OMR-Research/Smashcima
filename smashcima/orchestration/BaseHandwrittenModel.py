from .Model import Model
from ..geometry.Vector2 import Vector2
from ..loading.MusicXmlLoader import MusicXmlLoader
from ..synthesis.page.NaiveStafflinesSynthesizer \
    import NaiveStafflinesSynthesizer
from ..synthesis.page.StafflinesSynthesizer import StafflinesSynthesizer
from ..synthesis.layout.column.ColumnLayoutSynthesizer \
    import ColumnLayoutSynthesizer
from ..rendering.BitmapRenderer import BitmapRenderer
from ..synthesis.glyph.GlyphSynthesizer import GlyphSynthesizer
from ..synthesis.glyph.MuscimaPPGlyphSynthesizer import MuscimaPPGlyphSynthesizer
from smashcima.synthesis.page.SimplePageSynthesizer import SimplePageSynthesizer
from smashcima.synthesis.glyph.LineSynthesizer import LineSynthesizer
from smashcima.synthesis.glyph.NaiveLineSynthesizer \
    import NaiveLineSynthesizer
from smashcima.synthesis.glyph.MuscimaPPLineSynthesizer \
    import MuscimaPPLineSynthesizer
from smashcima.synthesis.layout.BeamStemSynthesizer import BeamStemSynthesizer
from smashcima.scene.visual.Page import Page
from smashcima.synthesis.style.MuscimaPPStyleDomain import MuscimaPPStyleDomain
from smashcima.synthesis.page.PaperSynthesizer import PaperSynthesizer
from smashcima.synthesis.page.SolidColorPaperSynthesizer \
    import SolidColorPaperSynthesizer
from smashcima.synthesis.page.MzkQuiltingPaperSynthesizer \
    import MzkQuiltingPaperSynthesizer
from smashcima.synthesis.style.MzkPaperStyleDomain \
    import MzkPaperStyleDomain
import numpy as np
from typing import List


class BaseHandwrittenModel(Model):
    """
    Model that serves as the basic handwritten music synthesizer.
    The whole framework is being developed around this model currently
    and its name might change in the future. It aims to be like Mashcima1
    with the additions of using MXL input, polyphony and postprocessing.
    """
    def __init__(self):
        super().__init__()

        self.pages: List[Page] = []
        "Pages that will be synthesized during model invocation"
    
    def register_services(self):
        super().register_services()
        c = self.container

        # TODO: there is some issue and the style domains are not being
        # resolved as singletons but as transients. Add unit tests,
        # maybe it has to do with a specific version of punq
        
        c.type(ColumnLayoutSynthesizer)
        c.type(BeamStemSynthesizer)
        c.interface(StafflinesSynthesizer, NaiveStafflinesSynthesizer)
        c.interface(GlyphSynthesizer, MuscimaPPGlyphSynthesizer)
        c.interface(LineSynthesizer, MuscimaPPLineSynthesizer)
        c.type(SimplePageSynthesizer)
        c.type(MuscimaPPStyleDomain)
        c.type(MzkPaperStyleDomain)
        # c.interface(PaperSynthesizer, SolidColorPaperSynthesizer)
        c.interface(PaperSynthesizer, MzkQuiltingPaperSynthesizer)

    def resolve_services(self):
        super().resolve_services()
        c = self.container

        self.layout_synthesizer = c.resolve(ColumnLayoutSynthesizer)
        self.page_synthesizer = c.resolve(SimplePageSynthesizer)
    
    def configure_services(self):
        super().configure_services()
        
        self.styler.register_domain(
            MuscimaPPStyleDomain,
            self.container.resolve(MuscimaPPStyleDomain)
        )
        self.styler.register_domain(
            MzkPaperStyleDomain,
            self.container.resolve(MzkPaperStyleDomain)
        )

    def __call__(self, annotation_file_path: str) -> np.ndarray:
        return super().__call__(annotation_file_path)

    def call(self, annotation_file_path: str):
        # load the symbolic part
        score = MusicXmlLoader().load_file(annotation_file_path)
        self.scene.add(score)

        # until you run out of music
        # 1. synthesize a page of stafflines
        # 2. fill the page with music
        self.pages = []
        next_measure_index = 0
        next_page_origin = Vector2(0, 0)
        _PAGE_SPACING = 10 # 1cm
        while next_measure_index < score.measure_count:
            # prepare the next page of music
            page = self.page_synthesizer.synthesize_page(next_page_origin)
            page.space.parent_space = self.scene.space
            self.scene.add(page)
            self.pages.append(page)

            next_page_origin += Vector2(
                page.view_box.rectangle.width + _PAGE_SPACING,
                0
            )

            # synthesize music onto the page
            systems = self.layout_synthesizer.fill_page(
                page,
                score,
                start_on_measure=next_measure_index
            )
            next_measure_index = systems[-1].last_measure_index + 1

        # add objects to scene that are transitively linked from objects
        # already in scene
        self.scene.add_closure()

        return self.render(page_index=0)
    
    def render(self, page_index: int) -> np.ndarray:
        renderer = BitmapRenderer()
        bitmap = renderer.render(self.scene, self.pages[page_index].view_box)
        return bitmap
