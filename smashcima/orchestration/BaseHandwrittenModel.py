import copy
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np

from smashcima.exporting.BitmapRenderer import BitmapRenderer
from smashcima.exporting.compositing.Compositor import Compositor
from smashcima.exporting.image.ImageLayer import ImageLayer
from smashcima.geometry import Vector2
from smashcima.loading import load_score
from smashcima.scene import AffineSpace, Page, Scene, Score
from smashcima.synthesis import (BeamStemSynthesizer,
                                 ColumnMusicNotationSynthesizer,
                                 GlyphSynthesizer, LineSynthesizer,
                                 MuscimaPPGlyphSynthesizer,
                                 MuscimaPPLineSynthesizer,
                                 MuscimaPPStyleDomain, MzkPaperStyleDomain,
                                 MzkQuiltingPaperSynthesizer,
                                 NaiveLineSynthesizer,
                                 NaiveStafflinesSynthesizer, PaperSynthesizer,
                                 SimplePageSynthesizer,
                                 SolidColorPaperSynthesizer,
                                 StafflinesSynthesizer)
from smashcima.synthesis.MusicNotationSynthesizer import \
    MusicNotationSynthesizer
from smashcima.synthesis.PageSynthesizer import PageSynthesizer
from smashcima.synthesis.style.MzkPaperStyleDomain import Patch

from .Model import Model


class BaseHandwrittenScene(Scene):
    """Scene synthesized by the `BaseHandwrittenModel`"""
    def __init__(
        self,
        root_space: AffineSpace,
        score: Score,
        mpp_writer: int,
        mzk_background_patch: Patch,
        pages: List[Page],
        compositor: Compositor
    ):
        super().__init__(root_space)
        
        self.score = score
        """The semantic score based on which the scene was synthesized"""

        self.mpp_writer = mpp_writer
        """The MUSCIMA++ writer number that was used for this scene"""

        self.mzk_background_patch = mzk_background_patch
        """The MZK texture patch used for the background paper"""

        self.pages = pages
        """All the pages of music that were synthesized"""

        self.compositor = compositor
        """The compositor to be used to flatten the scene into an image"""

        self.dpi: float = 300.0
        """The DPI at which to rasterize the scene"""

        self.__compositor_cache: Dict[int, ImageLayer] = {}
        """Caches composed image layers fr pages"""

        # add to the list of scene objects
        self.add_many([score, *pages])
    
    def compose_page(self, page: Page) -> ImageLayer:
        """Runs the given page through the compositor and returns the image.
        Caches the resulting image layer so that it can be used by multiple
        exporters without recomputing it many times over."""
        assert page in self.pages, "Given page is not in this scene"
        key = self.pages.index(page)

        if key not in self.__compositor_cache:
            self.__compositor_cache[key] \
                = self.compositor.run(page.view_box, dpi=self.dpi)

        return self.__compositor_cache[key]

    def render(self, page: Page) -> np.ndarray:
        """Renders the bitmap BGRA image of a page"""
        layer = self.compose_page(page)
        renderer = BitmapRenderer()
        return renderer.render(layer)


class BaseHandwrittenModel(Model[BaseHandwrittenScene]):
    """Synthesizes handwritten pages of music notation.

    This model provides similar functionality as MuseScore when it comes
    to rendering music content. You put in a musical content file
    (say MusicXML) and you get out a scene with a number of pages
    (depending on the music length and system and page breaks)
    and the scene can then be turn into an image and other annotations.
    
    This model acts as a flagship demonstrator for the Smashcima library.
    It serves as an example of what a well-designed Model looks like.
    """

    def register_services(self):
        super().register_services()
        c = self.container
        
        # stafflines
        c.interface(
            StafflinesSynthesizer, NaiveStafflinesSynthesizer, register_impl=True
        )

        # glyphs
        c.interface(
            GlyphSynthesizer, MuscimaPPGlyphSynthesizer, register_impl=True
        )
        c.interface(
            LineSynthesizer, MuscimaPPLineSynthesizer, register_impl=True
        )

        # notation
        c.type(ColumnMusicNotationSynthesizer)
        c.type(BeamStemSynthesizer)

        # page
        c.type(SimplePageSynthesizer)

        # style domains
        c.type(MuscimaPPStyleDomain)
        c.type(MzkPaperStyleDomain)

        # paper
        c.type(SolidColorPaperSynthesizer)
        c.type(MzkQuiltingPaperSynthesizer)

        # === interfaces ===

        # glyphs
        c.interface(GlyphSynthesizer, MuscimaPPGlyphSynthesizer)
        c.interface(LineSynthesizer, MuscimaPPLineSynthesizer)

        # notation
        c.interface(MusicNotationSynthesizer, ColumnMusicNotationSynthesizer)
        
        # page
        c.interface(PageSynthesizer, SimplePageSynthesizer)

        # paper
        c.interface(PaperSynthesizer, MzkQuiltingPaperSynthesizer)
        # c.interface(PaperSynthesizer, SolidColorPaperSynthesizer)

    def resolve_services(self):
        super().resolve_services()
        c = self.container

        self.notation_synthesizer = c.resolve(MusicNotationSynthesizer)
        self.page_synthesizer = c.resolve(PageSynthesizer)

        self.mpp_style_domain = c.resolve(MuscimaPPStyleDomain)
        self.mzk_paper_style_domain = c.resolve(MzkPaperStyleDomain)

    def __call__(
        self,
        file: Union[Path, str, None] = None,
        data: Union[bytes, str, None] = None,
        format: Optional[str] = None,
        score: Optional[Score] = None,
        clone_score: bool = False
    ) -> BaseHandwrittenScene:
        """Synthesizes handwritten pages given a musical content.
        
        The musical content can be provided as a file path, string data,
        or an already parsed Smashcima Score object. The content will
        be placed onto a page until it overflows and then another page is
        added - just like using MuseScore for MXL rendering.

        :param file: Path to a file with musical content
            (e.g. './my_file.musicxml')
        :param data: Musical contents as a bytes or string
            (e.g. MusicXML file contents)
        :param format: In what format is the musical content
            (file suffix, including the period, i.e. '.musicxml')
        :param score: Musical content in the form of an already parsed
            Smashcima Score
        :param clone_score: Should the score be cloned before being embedded
            in the resulting scene
        :returns: The synthesized scene with all the pages
        """

        # NOTE: This method is where input pre-processing should happen
        # and where the state of the model should be prepared for the
        # next synthesis invocation. For example, the Model base class
        # lets the styler pick specific styles here. Similarly, after the
        # synthesis core (the call() method) is invoked, this method is where
        # you can do any post-processing and updates to the model state.
        # For example, the Model base class sets the self.scene property here.

        if score is None:
            score = self.load_score(
                file=file,
                data=data,
                format=format
            )
        elif clone_score:
            score = copy.deepcopy(score)

        return super().__call__(score)

    def load_score(
        self,
        file: Union[Path, str, None] = None,
        data: Union[bytes, str, None] = None,
        format: Optional[str] = None,
    ) -> Score:
        """This method is responsible for loading input annotation files.
        
        Override this method to modify the loading behaviour.
        """
        return load_score(
            file=file,
            data=data,
            format=format
        )

    def call(self, score: Score) -> BaseHandwrittenScene:
        # NOTE: This method is where the synthesis itself happens and
        # the resulting scene is constructed. This method should not modify
        # the state of the model instance, these modifications should happen
        # in the __call__() method instead.

        root_space = AffineSpace()

        # until you run out of music
        # 1. synthesize a page of stafflines
        # 2. fill the page with music
        pages = []
        next_measure_index = 0
        next_page_origin = Vector2(0, 0)
        _PAGE_SPACING = 10 # 1cm
        while next_measure_index < score.measure_count:
            # prepare the next page of music
            page = self.page_synthesizer.synthesize_page(next_page_origin)
            page.space.parent_space = root_space
            pages.append(page)

            next_page_origin += Vector2(
                page.view_box.rectangle.width + _PAGE_SPACING,
                0
            )

            # synthesize music onto the page
            systems = self.notation_synthesizer.fill_page(
                page,
                score,
                start_on_measure=next_measure_index
            )
            next_measure_index = systems[-1].last_measure_index + 1

        # construct the complete scene and return
        return BaseHandwrittenScene(
            root_space=root_space,
            score=score,
            mpp_writer=self.mpp_style_domain.current_writer,
            mzk_background_patch=self.mzk_paper_style_domain.current_patch,
            pages=pages,
            compositor=self.compositor
        )
