from pathlib import Path
from typing import TypeVar, Type, Dict
from .AssetBundle import AssetBundle, BundleResolver
from ..config import MC_ASSETS_CACHE


T = TypeVar("T", bound=AssetBundle)


class AssetRepository(BundleResolver):
    """
    A folder on the local machine, where asset bundles are downloaded to
    and prepared. It also acts as the manager that installs and resolves
    asset bundles from this folder.
    """
    
    def __init__(self, path: Path):
        if path.exists() and not path.is_dir():
            raise Exception(
                f"The path at {path} has to be a directory or be non-existing."
            )
        
        self.path = path
        "Path to the asset repository folder"

        self.path.mkdir(parents=True, exist_ok=True)

        self._bundle_cache: Dict[Type[T], T] = dict()
        "Caches bundle instance to speed up their resolution"

    @staticmethod
    def default() -> "AssetRepository":
        """Builds a new instance of the default asset repository
        to use for this process"""
        return AssetRepository(
            Path(MC_ASSETS_CACHE).resolve()
        )
    
    def resolve_bundle(self, bundle_type: Type[T], force_install=False) -> T:
        """Ensures that a bundle is installed and returns its instance"""
        # try resolving from cache
        if bundle_type in self._bundle_cache:
            return self._bundle_cache[bundle_type]
        
        # instantiate the bundle
        bundle = bundle_type(
            bundle_directory=self.path / bundle_type.__name__,
            dependency_resolver=self
        )

        # cache the bundle instance
        self._bundle_cache[bundle_type] = bundle

        # run __post_init__ to resolve dependencies and do additional set-ups
        if hasattr(bundle, "__post_init__"):
            bundle.__post_init__()

        # do nothing if already installed
        if not bundle.needs_installation() and not force_install:
            return bundle
        
        print(f"[Smashcima Assets]: Installing bundle {bundle_type.__name__}...")

        # clear its directory
        bundle.remove()
        bundle.bundle_directory.mkdir()

        # run the installation
        bundle.install()

        # store metadata
        bundle.write_metadata()

        print(f"[Smashcima Assets]: Bundle {bundle_type.__name__} installed.")

        return bundle
