import copy
from pathlib import Path
from typing import List, Optional, Union

import numpy as np

from smashcima.geometry import Vector2
from smashcima.loading import load_score
from smashcima.rendering import BitmapRenderer
from smashcima.scene import AffineSpace, Page, Scene, Score
from smashcima.synthesis import (BeamStemSynthesizer, ColumnLayoutSynthesizer,
                                 LineSynthesizer, MuscimaPPGlyphSynthesizer,
                                 MuscimaPPLineSynthesizer,
                                 MuscimaPPStyleDomain, MzkPaperStyleDomain,
                                 MzkQuiltingPaperSynthesizer,
                                 NaiveLineSynthesizer,
                                 NaiveStafflinesSynthesizer, PaperSynthesizer,
                                 SimplePageSynthesizer,
                                 SolidColorPaperSynthesizer,
                                 StafflinesSynthesizer,
                                 GlyphSynthesizer)
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
        pages: List[Page]
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

        # add to the list of scene objects
        self.add_many([score, *pages])

    def render(self, page: Page, dpi=300) -> np.ndarray:
        """Renders the bitmap BGRA image of a page"""
        assert page in self.pages, "Given page is not in this scene"
        renderer = BitmapRenderer(dpi=dpi)
        bitmap = renderer.render(self, page.view_box)
        return bitmap


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

        self.mpp_style_domain = c.resolve(MuscimaPPStyleDomain)
        self.mzk_paper_style_domain = c.resolve(MzkPaperStyleDomain)
    
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
            systems = self.layout_synthesizer.fill_page(
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
            pages=pages
        )
