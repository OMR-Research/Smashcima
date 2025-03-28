import sys
from pathlib import Path

from smashcima.loading.MusicXmlLoader import MusicXmlLoader

from .BaseSharkTankCase import BaseSharkTankCase


class MusicXmlLoaderTest(BaseSharkTankCase):
    def run_loader(self, shark_path: Path):
        # just makes sure the loader does not crash
        loader = MusicXmlLoader(errout=sys.stdout)
        loader.load_file(shark_path)

    def test_music_xml_loader(self):
        self.run_loader(Path(
            "shark_tank/sharks/musicxml/20250212_omr-output-chords.musicxml"
        ))
        # self.execute_on_all_sharks(
        #     fixture=self.run_loader,
        #     sharks_folder=Path("sharks/musicxml")
        # )
