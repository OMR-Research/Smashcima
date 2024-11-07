from smashcima.geometry.Rectangle import Rectangle
from ..AssetBundle import AssetBundle
from ..download_file import download_file
from pathlib import Path
from tqdm import tqdm
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
import csv
import cv2


# TODO: pick more patches and cluster them up in a zip file
# that will be downloaded from github, with MZK only for budle development
# (so that the user does not get flagged for scraping MZK)


@dataclass
class Patch:
    mzk_uuid: str
    rectangle: Rectangle
    dpi: int

    def from_record(record: Tuple[str, str, str, str, str, str]) -> "Patch":
        return Patch(
            mzk_uuid=record[0],
            rectangle=Rectangle(
                x=int(record[1]),
                y=int(record[2]),
                width=int(record[3]),
                height=int(record[4]),
            ),
            dpi=int(record[5])
        )


class MzkPaperPatches(AssetBundle):
    def __post_init__(self):
        pass

    def install(self):
        print("Downloading MZK paper patches...")
        
        index = self.load_patch_index()
        for patch in tqdm(index):
            uuid = patch.mzk_uuid
            x = patch.rectangle.x
            y = patch.rectangle.y
            width = patch.rectangle.width
            height = patch.rectangle.height
            
            url = f"https://kramerius.mzk.cz/search/iiif/uuid:" \
                + f"{uuid}/{x},{y},{width},{height}/max/0/default.jpg"
            
            path = self.get_patch_path(patch)
            path.parent.mkdir(exist_ok=True, parents=True)
            
            download_file(url, path, with_progress_bar=False)
    
    @staticmethod
    def load_patch_index() -> List[Patch]:
        """Loads the list of patches from the CSV file"""
        index_path = Path(__file__).parent / "mzk_paper_patches.csv"
        
        index: List[Patch] = []
        with open(index_path, "r") as f:
            reader = csv.reader(f, delimiter=",", quotechar='"')
            
            # header
            assert next(reader) == ["uuid", "x", "y", "width", "height", "dpi"]
            
            # records
            for record in reader:
                index.append(Patch.from_record(record))
        
        return index
    
    def get_patch_path(self, patch: Patch) -> Path:
        """Returns path to the image file of the given patch"""
        uuid = patch.mzk_uuid
        x = patch.rectangle.x
        y = patch.rectangle.y
        w = patch.rectangle.width
        h = patch.rectangle.height
        dpi = patch.dpi
        filename = f"{uuid}_{x}_{y}_{w}_{h}_{dpi}.jpg"
        return self.bundle_directory / "patches" / filename

    def load_bitmap_for_patch(self, patch: Patch) -> np.ndarray:
        """Loads the patch image into the BGRA uint8 format used by
        Smashcima sprites"""
        path = self.get_patch_path(patch)

        # BGR only
        img = cv2.imread(str(path), cv2.IMREAD_COLOR)
        assert len(img.shape) == 3 # H, W, C
        assert img.shape[2] == 3 # B, G, R

        # add a non-transparent alpha channel
        alpha = np.full(
            shape=(img.shape[0], img.shape[1]),
            fill_value=255,
            dtype=np.uint8
        )
        img = np.stack(
            [img[:,:,0], img[:,:,1], img[:,:,2], alpha],
            axis=2
        )
        assert len(img.shape) == 3 # H, W, C
        assert img.shape[2] == 4 # B, G, R, A
        assert img.dtype == np.uint8

        return img
