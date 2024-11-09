from pathlib import Path
import numpy as np
import coolname
import random
import cv2


# useful global constant
REPO_FOLDER: Path = Path(__file__).parent.parent.resolve()


# dummy names for things
coolname.replace_random(random.Random(42))
def random_name() -> str:
    """Generates a random two-word name for things"""
    return " ".join(
        w.capitalize() for w in coolname.generate(2)
    )


# image conversions
def img_smashcima2gradio(img: np.ndarray) -> np.ndarray:
    # gradio uses RGB and smashcima uses BGRA
    return cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
