from ...AssetBundle import AssetBundle
from ...datasets.OmniOMRProto import OmniOMRProto
# from .SymbolRepository import SymbolRepository
from typing import Optional


class OmniOMRGlyphs(AssetBundle):
    def __post_init__(self) -> None:
        # self._symbol_repository_cache: Optional[SymbolRepository] = None

        self.omni_omr_proto = self.dependency_resolver.resolve_bundle(
            OmniOMRProto
        )

    def install(self):

        document_paths = list(
            self.omni_omr_proto.mung_directory.glob("*.xml")
        )

        # TODO ...
