from smashcima.assets.AssetRepository import AssetRepository
from smashcima.geometry.Vector2 import Vector2
from smashcima.orchestration.Container import Container
from smashcima.orchestration.OmniOMRModel import OmniOMRModel
from smashcima.scene.Glyph import Glyph
from smashcima.scene.LineGlyph import LineGlyph
from smashcima.synthesis.glyph.MuscimaPPGlyphSynthesizer import \
    MuscimaPPGlyphSynthesizer
from smashcima.synthesis.glyph.MuscimaPPLineSynthesizer import \
    MuscimaPPLineSynthesizer
from smashcima.synthesis.glyph.OmniOMRGlyphSynthesizer import \
    OmniOMRGlyphSynthesizer
from smashcima.synthesis.glyph.OmniOMRLineSynthesizer import \
    OmniOMRLineSynthesizer
from smashcima.synthesis.GlyphSynthesizer import GlyphSynthesizer
from smashcima.synthesis.LineSynthesizer import LineSynthesizer
from smashcima.synthesis.style.MuscimaPPStyleDomain import MuscimaPPStyleDomain
from smashcima.synthesis.style.MzkPaperStyleDomain import MzkPaperStyleDomain
from smashcima.synthesis.style.OmniOMRStyleDomain import OmniOMRStyleDomain
from smashcima.synthesis.style.StyleDomain import StyleDomain
from smashcima.synthesis.style.Styler import Styler

from .asset_bundles import ASSET_REPO, BackgroundSample, GlyphStyle


class DemoModel(OmniOMRModel):
    def register_services(self):
        super().register_services()

        # use one shared asset repository for the demo
        self.container.instance(AssetRepository, ASSET_REPO)

        # change the styler so that we disable style randomization
        self.container.factory(
            StaticStyler, lambda: StaticStyler(self.container)
        )
        self.container.interface(Styler, StaticStyler)

        # register the style domain that controls styles for the whole demo
        self.container.type(DemoStyleDomain)

        # regsiter and replace glyph synthesizers
        self.container.type(DemoGlyphSynthesizer)
        self.container.type(DemoLineSynthesizer)
        self.container.interface(GlyphSynthesizer, DemoGlyphSynthesizer)
        self.container.interface(LineSynthesizer, DemoLineSynthesizer)

        # NOTE: postprocessor is not used from the model,
        # but run externally in the demo because the demo lets you synthesize
        # a scene and then apply only the postprocessing step separately
    
    def resolve_services(self):
        super().resolve_services()

        # expose the style domain as a field
        self.demo_style_domain = self.container.resolve(DemoStyleDomain)


class StaticStyler(Styler):
    def pick_style(self):
        pass # do nothing, keep the current style unchanged


class DemoStyleDomain(StyleDomain):
    """Called before synthesis to set up all styles and synthesizer instances"""
    def __init__(
        self,
        container: Container,
        mpp_style_domain: MuscimaPPStyleDomain,
        omni_omr_style_domain: OmniOMRStyleDomain,
        mzk_paper_style_domain: MzkPaperStyleDomain
    ):
        self.container = container

        self.mpp_style_domain = mpp_style_domain
        self.omni_omr_style_domain = omni_omr_style_domain
        self.mzk_paper_style_domain = mzk_paper_style_domain

        self.glyph_synthesizer: GlyphSynthesizer \
            = self.container.resolve(MuscimaPPGlyphSynthesizer) # default value
        self.line_synthesizer: LineSynthesizer \
            = self.container.resolve(MuscimaPPLineSynthesizer) # default value

    def pick_style(self):
        pass # randomization would be here, but it's disbled in styler anyways

    def apply_glyph_style(self, glyph_style: GlyphStyle):
        """Called before synthesis to set the current glyph style"""
        c = self.container
        if glyph_style.dataset == "muscima_pp":
            self.glyph_synthesizer = c.resolve(MuscimaPPGlyphSynthesizer)
            self.line_synthesizer = c.resolve(MuscimaPPLineSynthesizer)
            self.mpp_style_domain.current_style = glyph_style.style
        elif glyph_style.dataset == "omni_omr":
            self.glyph_synthesizer = c.resolve(OmniOMRGlyphSynthesizer)
            self.line_synthesizer = c.resolve(OmniOMRLineSynthesizer)
            self.omni_omr_style_domain.current_style = glyph_style.style
        else:
            raise Exception(f"Unknown dataset: {glyph_style.dataset}")
    
    def apply_paper_style(self, sample: BackgroundSample):
        self.mzk_paper_style_domain.current_patch = sample.patch


class DemoGlyphSynthesizer(GlyphSynthesizer):
    """Forwards calls to the synthesizer from the DemoStyleDomain"""
    def __init__(self, style_domain: DemoStyleDomain):
        self.style_domain = style_domain

    def supports_label(self, label: str) -> bool:
        return self.style_domain.glyph_synthesizer.supports_label(label)
    
    def create_glyph(self, label: str) -> Glyph:
        return self.style_domain.glyph_synthesizer.create_glyph(label)


class DemoLineSynthesizer(LineSynthesizer):
    """Forwards calls to the synthesizer from the DemoStyleDomain"""
    def __init__(self, style_domain: DemoStyleDomain):
        self.style_domain = style_domain
    
    def supports_label(self, label: str) -> bool:
        return self.style_domain.line_synthesizer.supports_label(label)

    def create_glyph(self, label: str, delta: Vector2) -> LineGlyph:
        return self.style_domain.line_synthesizer.create_glyph(label, delta)
