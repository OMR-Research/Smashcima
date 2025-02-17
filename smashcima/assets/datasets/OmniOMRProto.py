import time
from ..AssetBundle import AssetBundle
import zipfile
from pathlib import Path


ZIP_FILE_NAME = "2024-10-07_proto-dataset.zip"


class OmniOMRProto(AssetBundle):
    def install(self) -> None:
        zip_path: Path = self.bundle_directory / ZIP_FILE_NAME

        print("Locating the zip file...")
        self._wait_for_zip_to_appear(zip_path)

        print("Extracting the zip file...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(self.bundle_directory)
        
        print("Checking bundle directory structure...")
        assert (self.bundle_directory / "2024-10-07_proto-dataset").is_dir()
        assert (self.bundle_directory / "2024-10-07_proto-dataset" / "MuNG").is_dir()
        assert (self.bundle_directory / "2024-10-07_proto-dataset" / "images").is_dir()
    
    def _wait_for_zip_to_appear(self, zip_path: Path) -> None:
        """
        Spins untill the zip file is placed by the user into the bundle folder.
        """
        if zip_path.is_file():
            return
        
        print("\n!!! ACTION NEEDED !!!")
        print(
            "Please place the OmniOMR proto dataset zip into the bundle " +
            "directory for the installation to continue. The expected " +
            "placement is:\n" + str(zip_path.absolute())
        )
        while not zip_path.is_file():
            time.sleep(1)
        
        print("Thank you! The installation continues...")
    
    @property
    def mung_directory(self) -> Path:
        """Returns path to the directory with all MuNG XMLs"""
        return self.bundle_directory / "2024-10-07_proto-dataset" / "MuNG"
