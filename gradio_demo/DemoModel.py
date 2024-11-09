from smashcima.orchestration.BaseHandwrittenModel import BaseHandwrittenModel
from smashcima.synthesis.style.MzkPaperStyleDomain import MzkPaperStyleDomain
from smashcima.synthesis.style.MuscimaPPStyleDomain import MuscimaPPStyleDomain
from smashcima.synthesis.style.Styler import Styler
from smashcima.assets.AssetRepository import AssetRepository
from .asset_bundles import ASSET_REPO


class StaticStyler(Styler):
    def pick_style(self):
        pass # do nothing, keep the current style unchanged


class DemoModel(BaseHandwrittenModel):
    def register_services(self):
        super().register_services()

        # change the styler used by the model
        self.container.interface(Styler, StaticStyler)

        # use one shared asset repository for the demo
        self.container.instance(AssetRepository, ASSET_REPO)
    
    def resolve_services(self):
        super().resolve_services()

        # keep style domains as fields
        self.mpp_style_domain = self.container.resolve(MuscimaPPStyleDomain)
        self.paper_style_domain = self.container.resolve(MzkPaperStyleDomain)
