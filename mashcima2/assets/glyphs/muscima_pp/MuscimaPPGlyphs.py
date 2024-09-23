from ...AssetBundle import AssetBundle
from ...datasets.MuscimaPP import MuscimaPP
from .MppPage import MppPage
from .get_symbols import get_whole_notes, get_black_noteheads
from .SymbolRepository import SymbolRepository
from pathlib import Path
import pickle


class MuscimaPPGlyphs(AssetBundle):
    def __post_init__(self):
        self.muscima_pp = self.dependency_resolver.resolve_bundle(MuscimaPP)

    @property
    def symbol_repository_path(self) -> Path:
        return self.bundle_directory / "symbol_repository.pkl"
    
    def install(self):
        document_paths = list(
            self.muscima_pp.cropobjects_directory.glob("CVC-MUSCIMA_*-ideal.xml")
        )

        repository = SymbolRepository()

        # TODO: for each document
        for document_path in document_paths:
            page = MppPage.load(document_path)

            black_noteheads = get_black_noteheads(page)
            whole_notes = get_whole_notes(page)
            
            repository.black_noteheads += black_noteheads
            repository.whole_notes += whole_notes

            if len(black_noteheads) > 0:
                break
        
        # TODO: store all glyphs in a pickle that can then be loaded
        # on-request by a MPP glyph synthesizer

        with open(self.symbol_repository_path, "wb") as file:
            pickle.dump(repository, file)
            print("Writing...", self.symbol_repository_path)
        
        # TODO: DEBUG
        self.repository = repository
    
    def load_symbol_repository(self) -> SymbolRepository:
        with open(self.symbol_repository_path, "rb") as file:
            repository = pickle.load(file)
        assert isinstance(repository, SymbolRepository)
        return repository


if __name__ == "__main__":
    print("Re-installing MUSCIMA++ glyphs...")
    from ...AssetRepository import AssetRepository
    from pathlib import Path
    assets = AssetRepository(Path("mashcima_assets"))
    assets.resolve_bundle(MuscimaPPGlyphs, force_install=True)
    print("Done.")