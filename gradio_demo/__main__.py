from .asset_bundles import MXL_FILES, WRITERS, BACKGROUND_SAMPLES
from .utils import img_smashcima2gradio
from .DemoModel import DemoModel
from typing import Optional
import gradio as gr
import numpy as np
import random


with gr.Blocks() as demo:
    
    # === state ===

    model_cache = gr.State(None)
    "Holds the model instance for the user session"

    background = gr.State(0)
    "The index of the selected background sample"

    # === components ===

    gr.Markdown("""
        # Smashcima Demo
        
        GitHub: https://github.com/OMR-Research/Smashcima
        
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

    def synthesize(
        model: Optional[DemoModel],
        mxl_file_name: str,
        writer: int,
        bg_index: int
    ) -> np.ndarray:
        # create the model with the first user request
        if model is None:
            model = DemoModel()

        # full path to the input MusicXML file
        mxl_path = str(next(f for f in MXL_FILES if f.name == mxl_file_name))

        # set the writer style
        model.mpp_style_domain.current_writer = writer

        # set the background paper style
        model.paper_style_domain.current_patch \
            = BACKGROUND_SAMPLES[bg_index].patch

        # run the synthesizer
        img = model(mxl_path)

        return img_smashcima2gradio(img), model
    
    # === bind events ===

    synth_evt_args = (
        synthesize,
        [model_cache, mxl_file_radio, writer_radio, background],
        [output_canvas, model_cache]
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
