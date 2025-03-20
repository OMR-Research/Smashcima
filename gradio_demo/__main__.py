import copy
import random
from typing import List, Optional, Tuple

import gradio as gr
import numpy as np

from smashcima.exporting.BitmapRenderer import BitmapRenderer
from smashcima.exporting.compositing.DefaultCompositor import DefaultCompositor
from smashcima.exporting.postprocessing.BaseHandwrittenPostprocessor import \
    BaseHandwrittenPostprocessor
from smashcima.exporting.postprocessing.Filter import Filter
from smashcima.orchestration.BaseHandwrittenModel import BaseHandwrittenScene
from smashcima.scene.Glyph import Glyph
from smashcima.scene.Sprite import Sprite
from smashcima.scene.semantic.Part import Part
from smashcima.scene.visual import RestVisual
from smashcima.scene.visual.Notehead import Notehead
from smashcima.scene.visual.Page import Page

from .asset_bundles import BACKGROUND_SAMPLES, MXL_FILES, GLYPH_STYLES
from .DemoModel import DemoModel
from .utils import img_smashcima2gradio


POSTPROCESSING_FILTERS = [
    # (filter name, display label)
    ("f_stafflines", "Stafflines"),
    ("f_scribbles", "Scribbles"),
    ("f_folding", "Folding"),
    ("f_camera", "Camera effects"),
    ("f_inkstyle", "Ink texture"),
    ("f_bleed_through", "Bleed through"),
    ("f_ink_color", "Ink color"),
]


with gr.Blocks() as demo:
    
    # === state ===

    model_state = gr.State(None)
    """Holds the model instance for the user session"""

    background_state = gr.State(0)
    """The index of the selected background sample"""

    scene_state = gr.State(None)
    """The synthesized scene that has yet to be converted to an image"""

    # === components ===

    gr.Markdown("""
        # Smashcima Demo
        
        GitHub: https://github.com/OMR-Research/Smashcima
        
        Start by pressing the **Synthesize** button. Then you can play
        with the settings below and re-try to see the effect.
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            synthesize_btn = gr.Button("Synthesize ↱", variant="primary")
            randomize_btn = gr.Button("Randomize")

            with gr.Accordion("Input MusicXML Files", open=False):
                mxl_file_radio = gr.Radio(
                    label=None,
                    container=False,
                    choices=[p.name for p in MXL_FILES],
                    value=MXL_FILES[0].name
                )
            
            with gr.Accordion("Glyph Style", open=False):
                gr.Markdown("""
                    There are two symbol repositories: MUSCIMA++ and OmniOMR
                    proto dataset. MUSCIMA++ has 50 writers with labels `w01`
                    up to `w50`. OmniOMR is a collection of pages from books,
                    where each book as a UUID, e.g. `1d507bc2`.
                    
                    Here are interesting styles to try:
                    - `w01` The default, clean writer.
                    - `w28` Has big and round noteheads.
                    - `afa71e12` Is a 19th century, quill-written document.
                    - `334c2e20` Is a typeset (printed) document.
                """)
                glyph_style_radio = gr.Radio(
                    label=None,
                    container=False,
                    choices=[s.title for s in GLYPH_STYLES],
                    value=GLYPH_STYLES[0].title,
                    type="index"
                )

            with gr.Accordion("Paper Texture", open=False):
                gr.Markdown(
                    value=lambda b: \
                        f"Currently selected: {BACKGROUND_SAMPLES[b].title}",
                    inputs=[background_state]
                )
                background_gallery = gr.Gallery(
                    label=None,
                    container=False,
                    columns=3,
                    value=[(s.gradio_image, s.title) for s in BACKGROUND_SAMPLES],
                    interactive=False, # disable user's uploads
                )

        with gr.Column(scale=1):
            scene_info_md = gr.Markdown(
                "*(there is no synthesized scene yet)*"
            )

            with gr.Accordion("Postprocessing Filters", open=False):
                postprocessing_radio = gr.Radio(
                    label=None,
                    container=False,
                    choices=["random", "manual"],
                    value="random"
                )
                postprocessing_checkboxes = gr.CheckboxGroup(
                    label="Manual Postprocessing Filters",
                    choices=[l for f, l in POSTPROCESSING_FILTERS],
                    value=[],
                    type="index"
                )

            scene_preview_image = gr.Image(
                label="Synthesized Scene Preview",
                format="jpeg"
            )
        
        with gr.Column(scale=1):
            render_btn = gr.Button("Render ↴")

            final_image = gr.Image(
                label="Final Image",
                format="jpeg"
            )

    # === event handlers ===

    def change_background(select_data: gr.SelectData) -> int:
        return select_data.index
    
    def randomize():
        new_mxl_file_name = random.choice(MXL_FILES).name
        new_glyph_style = random.choice(GLYPH_STYLES)
        new_background = random.randint(0, len(BACKGROUND_SAMPLES) - 1)
        return (
            gr.Radio(value=new_mxl_file_name),
            gr.Radio(value=new_glyph_style.title),
            gr.Gallery(selected_index=new_background)
        )

    def synthesize_scene(
        model: Optional[DemoModel],
        mxl_file_name: str,
        glyph_style_index: int,
        background: int
    ) -> Tuple[np.ndarray, DemoModel, str]:
        # create the model with the first user request
        if model is None:
            model = DemoModel()

        # full path to the input MusicXML file
        mxl_path = str(next(f for f in MXL_FILES if f.name == mxl_file_name))

        # set the glyph style
        model.demo_style_domain.apply_glyph_style(
            GLYPH_STYLES[glyph_style_index]
        )

        # set the background paper style
        model.demo_style_domain.apply_paper_style(
            BACKGROUND_SAMPLES[background]
        )
        
        # run the synthesizer
        scene = model(mxl_path)

        # create the preview image
        scene_copy = copy.deepcopy(scene)
        for g in scene_copy.find(Glyph):
            Sprite.debug_box(
                g.space,
                g.get_bbox_in_space(g.space),
                fill_color=(0, 0, 255, 32),
                border_color=(0, 0, 255, 128),
                border_width=0.4
            )
        scene_preview_img = BitmapRenderer.default_viewbox_render(
            view_box=scene_copy.pages[0].view_box,
            dpi=300
        )

        return (
            scene,
            model,
            img_smashcima2gradio(scene_preview_img),
            f"""
            Scene Objects: {len(scene.objects)},
            Glyphs: {len(scene.find(Glyph))}<br>
            Pages: {len(scene.find(Page))},
            Parts: {len(scene.find(Part))}<br>
            Noteheads: {len(scene.find(Notehead))},
            Rests: {len(scene.find(RestVisual))}<br>
            """
        )
    
    def render_final_image(
        scene: Optional[BaseHandwrittenScene],
        radio: str,
        checkboxes: List[int]
    ) -> np.ndarray:
        if scene is None:
            raise gr.Error("You must synthesize a scene first.")

        rng = random.Random()
        pp = BaseHandwrittenPostprocessor(rng)
        compositor = DefaultCompositor(pp)

        # configure the postprocessor
        for i, (filter_name, _) in enumerate(POSTPROCESSING_FILTERS):
            filter: Filter = getattr(pp, filter_name)
            if radio == "manual":
                filter.force_do = (i in checkboxes)
                filter.force_dont = (i not in checkboxes)
            else:
                filter.force_do = False
                filter.force_dont = False
        
        # produce the postprocessed final image
        layer = compositor.run(scene.pages[0].view_box, dpi=300)
        renderer = BitmapRenderer()
        final_img = renderer.render(layer)

        return img_smashcima2gradio(final_img)
    
    # === bind events ===

    synth_evt_args = (
        synthesize_scene,
        [model_state, mxl_file_radio, glyph_style_radio, background_state],
        [scene_state, model_state, scene_preview_image, scene_info_md]
    )

    render_evt_args = (
        render_final_image,
        [scene_state, postprocessing_radio, postprocessing_checkboxes],
        [final_image]
    )

    randomize_btn.click(
        randomize, [],
        [mxl_file_radio, glyph_style_radio, background_gallery]
    )
    background_gallery.select(change_background, [], [background_state])
    synthesize_btn.click(*synth_evt_args)
    scene_state.change(*render_evt_args)
    render_btn.click(*render_evt_args)


# .venv/bin/python3 -m gradio_demo
if __name__ == "__main__":
    demo.launch()
