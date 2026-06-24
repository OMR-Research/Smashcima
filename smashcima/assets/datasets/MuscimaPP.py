from ..AssetBundle import AssetBundle
from ..download_file import download_file
import zipfile
from pathlib import Path


DOWNLOAD_URL = "https://lindat.mff.cuni.cz/repository/server/api/core/bitstreams/handle/11372/LRT-2372/MUSCIMA-pp_v1.0.zip"


class MuscimaPP(AssetBundle):
    def install(self):
        print("Downloading MUSCIMA++ dataset...")
        downloaded_zip = self.bundle_directory / "MUSCIMA-pp_v1.0.zip"
        download_file(
            DOWNLOAD_URL,
            downloaded_zip
        )

        print("Extracting the zip...")
        with zipfile.ZipFile(downloaded_zip, "r") as zip_ref:
            zip_ref.extractall(self.bundle_directory)
        downloaded_zip.unlink()

        print("Checking bundle directory structure...")
        assert (self.bundle_directory / "v1.0").is_dir()
        assert (self.bundle_directory / "v1.0" / "data").is_dir()
        assert (
            self.bundle_directory / "v1.0" / "data" / "cropobjects_withstaff"
        ).is_dir()
        assert (self.cropobjects_directory).is_dir()
    
    @property
    def cropobjects_directory(self) -> Path:
        """Returns path to the directory with all cropobject XMLs"""
        return self.bundle_directory / "v1.0" / "data" / "cropobjects_withstaff"
