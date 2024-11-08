from smashcima.orchestration.BaseHandwrittenModel import BaseHandwrittenModel
from smashcima.synthesis.style.MzkPaperStyleDomain import MzkPaperStyleDomain
from smashcima.synthesis.style.MuscimaPPStyleDomain import MuscimaPPStyleDomain
from smashcima.synthesis.style.Styler import Styler
from smashcima.assets.AssetRepository import AssetRepository
from smashcima.assets.textures.MzkPaperPatches import MzkPaperPatches, Patch
from smashcima.assets.glyphs.muscima_pp.MuscimaPPGlyphs import MuscimaPPGlyphs
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
# Smashcima Initialization #
############################

ASSET_REPO = AssetRepository(REPO_FOLDER / "smashcima_assets")


class StaticStyler(Styler):
    def pick_style(self):
        pass # do nothing, keep the current style unchanged


class DemoModel(BaseHandwrittenModel):
    def register_services(self):
        super().register_services()

        # change the styler used by the model
        self.container.interface(Styler, StaticStyler)

        # use one shared asset repository for the demo
        self.container.instance(AssetRepository, ASSET_REPO)
    
    def resolve_services(self):
        super().resolve_services()

        # keep style domains as fields
        self.mpp_style_domain = self.container.resolve(MuscimaPPStyleDomain)
        self.paper_style_domain = self.container.resolve(MzkPaperStyleDomain)


model = DemoModel()


#################
# Writer Styles #
#################

mpp_glyphs = ASSET_REPO.resolve_bundle(MuscimaPPGlyphs)
mpp_symbol_repo = mpp_glyphs.load_symbol_repository()
WRITERS = list(sorted(mpp_symbol_repo.all_writers))


######################
# Background Samples #
######################


@dataclass
class BackgroundSample:
    patch: Patch
    title: str
    gradio_image: np.ndarray


paper_patches_bundle = ASSET_REPO.resolve_bundle(MzkPaperPatches)

BACKGROUND_SAMPLES: List[BackgroundSample] = [
    BackgroundSample(
        patch=patch,
        title=random_name(),
        gradio_image=img_smashcima2gradio(
            paper_patches_bundle.load_bitmap_for_patch(patch)
        )
    )
    for patch in paper_patches_bundle.load_patch_index()
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
                label="Input MusicXML Files",
                choices=[p.name for p in MXL_FILES],
                value=MXL_FILES[0].name
            )
            
            with gr.Accordion("Style Controls", open=False):
                writer_radio = gr.Radio(
                    label="Handwriting Style",
                    choices=WRITERS,
                    value=WRITERS[0]
                )

                background_gallery = gr.Gallery(
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
    
    def randomize():
        new_mxl_file_name = random.choice(MXL_FILES).name
        new_writer = random.choice(WRITERS)
        new_bg_index = random.randint(0, len(BACKGROUND_SAMPLES) - 1)
        return (
            gr.Radio(value=new_mxl_file_name),
            gr.Radio(value=new_writer),
            gr.Gallery(selected_index=new_bg_index)
        )

    def synthesize(mxl_file_name: str, writer: int, bg_index: int) -> np.ndarray:
        global model
        # TODO: keep the model instance in session state

        mxl_path = str(next(f for f in MXL_FILES if f.name == mxl_file_name))

        # set the writer style
        model.mpp_style_domain.current_writer = writer

        # set the background paper style
        model.paper_style_domain.current_patch \
            = BACKGROUND_SAMPLES[bg_index].patch

        img = model(mxl_path)
        return img_smashcima2gradio(img)
    
    # === bind events ===

    synth_evt_args = (
        synthesize,
        [mxl_file_radio, writer_radio, background],
        [output_canvas]
    )

    randomize_btn.click(
        randomize, [],
        [mxl_file_radio, writer_radio, background_gallery]
    )
    synthesize_btn.click(*synth_evt_args)
    mxl_file_radio.change(*synth_evt_args)
    writer_radio.change(*synth_evt_args)
    background_gallery.select(change_background, [], [background]) \
        .then(*synth_evt_args)


# .venv/bin/python3 -m gradio_demo
if __name__ == "__main__":
    demo.launch()
