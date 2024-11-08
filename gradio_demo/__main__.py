from smashcima.orchestration.BaseHandwrittenModel import BaseHandwrittenModel
from smashcima.synthesis.style.MzkPaperStyleDomain import MzkPaperStyleDomain
from smashcima.assets.AssetRepository import AssetRepository
from smashcima.assets.textures.MzkPaperPatches import MzkPaperPatches, Patch
from pathlib import Path
from dataclasses import dataclass
from typing import List
import cv2
import gradio as gr
import random
import coolname
import numpy as np

REPO_FOLDER: Path = Path(__file__).parent.parent.resolve()

coolname.replace_random(random.Random(42))

def random_name() -> str:
    return " ".join(
        w.capitalize() for w in coolname.generate(2)
    )

def img_smashcima2gradio(img: np.ndarray) -> np.ndarray:
    # gradio uses RGB and smashcima uses BGRA
    return cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)


############################
# Smashcima initialization #
############################

model = BaseHandwrittenModel()
assets = model.container.resolve(AssetRepository)
paper_patches_bundle = assets.resolve_bundle(MzkPaperPatches)
paper_style_domain = model.styler.resolve_domain(MzkPaperStyleDomain)


######################
# Background Samples #
######################

@dataclass
class BackgroundSample:
    patch: Patch
    title: str
    gradio_image: np.ndarray

BACKGROUND_SAMPLES: List[BackgroundSample] = [
    BackgroundSample(
        patch=patch,
        title=random_name(),
        gradio_image=img_smashcima2gradio(
            paper_patches_bundle.load_bitmap_for_patch(patch)
        )
    )
    for patch in paper_style_domain.all_patches
]


########################
# Input MusicXML Files #
########################

MXL_FILES: List[Path] = [
    REPO_FOLDER / "testing" / "lc6247269.musicxml", # TODO: move into the demos folder
    REPO_FOLDER / "jupyter" / "layout_synthesis" / "notehead_placement.musicxml",
    REPO_FOLDER / "jupyter" / "layout_synthesis" / "rests.musicxml",
    REPO_FOLDER / "jupyter" / "layout_synthesis" / "stems.musicxml",
    REPO_FOLDER / "jupyter" / "layout_synthesis" / "beams.musicxml",
    REPO_FOLDER / "jupyter" / "layout_synthesis" / "flags.musicxml",
    REPO_FOLDER / "jupyter" / "layout_synthesis" / "ledger_lines.musicxml",
    REPO_FOLDER / "jupyter" / "layout_synthesis" / "duration_dots.musicxml",
    REPO_FOLDER / "jupyter" / "layout_synthesis" / "accidentals.musicxml",
]


#################
# Define the UI #
#################

with gr.Blocks() as demo:
    
    # === state ===

    background = gr.State(0)
    "The index of the selected background sample"

    # === components ===

    gr.Markdown("""
        # Smashcima Demo
        
        Start by pressing the **Synthesize** button. Then you can play
        with the settings below and re-try to see the effect.
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Row():
                randomize_btn = gr.Button("Randomize")
                synthesize_btn = gr.Button("Synthesize", variant="primary")

            mxl_file_radio = gr.Radio(
                label="Input MusicXML files",
                choices=[p.name for p in MXL_FILES],
                value=MXL_FILES[0].name
            )

            gallery = gr.Gallery(
                label="Background Sample",
                columns=3,
                value=[(s.gradio_image, s.title) for s in BACKGROUND_SAMPLES],
                interactive=False, # disable user's uploads
            )

        with gr.Column(scale=1):
            output_canvas = gr.Image(
                label="Synthesized Image",
                format="jpeg"
            )

    # === event handlers ===

    def change_background(select_data: gr.SelectData) -> int:
        return select_data.index

    def synthesize(bg_index: int, mxl_file_name: str) -> np.ndarray:
        path = next(f for f in MXL_FILES if f.name == mxl_file_name)
        print("Render:", bg_index, path)
        # TODO: modify the model style according to arguments
        # TODO: keep the model instance in session state
        # TODO: have one instance of AssetRepository that points to this repo
        img = model(str(path))
        return img_smashcima2gradio(img)
    
    # === bind events ===

    synth_evt_args = (
        synthesize,
        [background, mxl_file_radio],
        [output_canvas]
    )

    gallery.select(change_background, [], [background]).then(*synth_evt_args)
    synthesize_btn.click(*synth_evt_args)


# .venv/bin/python3 -m gradio_demo
if __name__ == "__main__":
    demo.launch()
