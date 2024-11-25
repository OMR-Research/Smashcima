import abc
import json
import shutil
from pathlib import Path
from typing import Any, Dict, Type, TypeVar

from .._version import SMASHCIMA_VERSION_STR

T = TypeVar("T", bound="AssetBundle")


class BundleResolver(abc.ABC):
    """Interface representing something that can resolve asset bundles"""
    
    @abc.abstractmethod
    def resolve_bundle(self, bundle_type: Type[T]) -> T:
        """Ensures that a bundle is installed and returns its instance"""
        raise NotImplementedError


BUNDLE_META_FILE = "bundle.json"


class AssetBundle(abc.ABC):
    """
    Base class representing an asset bundle.
    
    Asset is any piece of external data, which can be used during syntehsis.
    This can be a MUSCIMA++ symbol mask, trained generative ML model,
    or some aggregated distribution.

    Asset bundle is a group of these assets that is downloaded, unpacked,
    and used as a single unit. It is a "library of assets".
    """
    def __init__(
        self,
        bundle_directory: Path,
        dependency_resolver: BundleResolver
    ):
        assert isinstance(bundle_directory, Path)
        self.bundle_directory = bundle_directory
        "Path to the directory where the bundle should be installed"

        self.dependency_resolver = dependency_resolver
        "Use this to resolve additional bundle dependencies"
    
    def version(self) -> Any:
        """Returns version of this bundle. Override this method to modify.
        
        Bundle versions should be incremented to trigger bundle re-install
        for all users who have this bundle already installed. This is useful
        whenever the bundle folder structure changes, or the pickled types
        change.

        Although this should primarily be incrementing integers to trigger
        cache busing, you can return anything that can be serialized to JSON
        and stored in the meta file. Therefore if your bundle requires
        more complex versioning, you can use strings or tuples.
        """
        return 1

    @abc.abstractmethod
    def install(self):
        """Downloads and installs the bundle into the bundle directory."""
        raise NotImplementedError
    
    def remove(self):
        """Removes the bundle from the asset repository folder"""
        shutil.rmtree(self.bundle_directory, ignore_errors=True)
        assert not self.bundle_directory.exists()
    
    def write_metadata(self):
        """Writes the metadata file for the bundle"""
        metadata = {
            # more metadata can be added in the future,
            # such as install datetime, install smashcima version, etc.
            "installed": True,
            "smashcima_version": SMASHCIMA_VERSION_STR,
            "version": self.version()
        }
        with open(self.bundle_directory / BUNDLE_META_FILE, "w") as f:
            json.dump(metadata, f)
    
    def needs_installation(self) -> bool:
        """Returns true if the bundle should be (re-)installed before use"""
        # if there's no metadata file, it probably is not even installed,
        # we definitely need to install before use
        if not self.metadata_exists():
            return True
        
        # load bundle metadata
        with open(self.bundle_directory / BUNDLE_META_FILE, "r") as f:
            metadata: Dict[str, Any] = json.load(f)
        
        # if smashcima version changed, we need re-install, because there
        # might be pickles with old type versions from the library
        if metadata.get("smashcima_version") != SMASHCIMA_VERSION_STR:
            return True
        
        # if bundle version changed, we also need to re-install
        if metadata.get("version") != self.version():
            return True

        return False
    
    def metadata_exists(self) -> bool:
        """Returns true if the metadata file exists for the bundle"""
        return (self.bundle_directory / BUNDLE_META_FILE).is_file()
