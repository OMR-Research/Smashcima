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
from smashcima.synthesis.style.OmniOMRStyleDomain import OmniOMRStyleDomain

from .BaseHandwrittenModel import BaseHandwrittenModel


class OmniOMRModel(BaseHandwrittenModel):
    def register_services(self):
        super().register_services()

        # additional style domain
        self.container.type(OmniOMRStyleDomain)
        
        # additional glyph synthesizers
        self.container.type(OmniOMRGlyphSynthesizer)
        self.container.type(OmniOMRLineSynthesizer)

        # re-bind glyph synthesizer interfaces
        self.container.interface(GlyphSynthesizer, OmniOMRGlyphSynthesizer)
        self.container.interface(LineSynthesizer, OmniOMRLineSynthesizer)

    def resolve_services(self) -> None:
        super().resolve_services()
        c = self.container
    
        self.omni_omr_glyph_synthesizer = c.resolve(OmniOMRGlyphSynthesizer)
        self.omni_omr_line_synthesizer = c.resolve(OmniOMRLineSynthesizer)
        
        self.muscima_pp_glyph_synthesizer = c.resolve(MuscimaPPGlyphSynthesizer)
        self.muscima_pp_line_synthesizer = c.resolve(MuscimaPPLineSynthesizer)
        
        self.omni_omr_style_domain = c.resolve(OmniOMRStyleDomain)

    def configure_services(self):
        super().configure_services()

        # configure the fallback synthesizer
        self.omni_omr_glyph_synthesizer.fallback_synthesizer \
            = self.muscima_pp_glyph_synthesizer
        self.omni_omr_line_synthesizer.fallback_synthesizer \
            = self.muscima_pp_line_synthesizer
