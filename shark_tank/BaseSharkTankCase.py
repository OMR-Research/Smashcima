from pathlib import Path
import unittest
from typing import Callable


class BaseSharkTankCase(unittest.TestCase):
    def execute_on_all_sharks(
        self,
        fixture: Callable[[Path], None],
        sharks_folder: Path
    ):
        """Runs a function on all sharks in a given folder.
        
        :param fixture: The function to be called on each shark.
        :param sharks_folder: The specific sub-folder with shark files,
            relative to the /shark_tank folder
        """
        shark_tank = Path(__file__).parent.resolve()
        folder_path = shark_tank / sharks_folder

        print(flush=True)
        for shark in folder_path.iterdir():
            print(
                "  >-shark°>",
                shark.relative_to(shark_tank),
                "...",
                end="",
                flush=True
            )
            
            fixture(shark)

            print(" ok", flush=True)
        
        print("  => ", end="", flush=True)
